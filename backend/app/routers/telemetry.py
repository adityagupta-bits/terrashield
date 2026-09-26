from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import SensorNode, TelemetryRecord, IncidentAlert
from app.schemas import TelemetryIngest, TelemetryResponse, AIPredictionResponse
from app.ai_engine import ai_engine
from app.alert_dispatcher import alert_dispatcher
from app.websocket_manager import ws_manager
from app.config import settings

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

@router.post("/ingest", response_model=dict)
async def ingest_telemetry(payload: TelemetryIngest, db: Session = Depends(get_db)):
    """
    Ingests sensor telemetry packets from physical ESP32 edge gateways or the simulator.
    Processes on-the-fly AI rate-of-change and threshold calculations.
    """
    # Verify or update node record
    node = db.query(SensorNode).filter(SensorNode.id == payload.node_id).first()
    if not node:
        node = SensorNode(
            id=payload.node_id,
            name=f"Edge Node {payload.node_id}",
            latitude=settings.DEFAULT_LAT,
            longitude=settings.DEFAULT_LNG,
            status="ONLINE",
            hop_count=payload.mesh_hops,
            parent_node_id=payload.parent_node_id
        )
        db.add(node)
    
    node.last_seen = datetime.utcnow()
    node.hop_count = payload.mesh_hops
    if payload.parent_node_id:
        node.parent_node_id = payload.parent_node_id
    if payload.battery_pct is not None:
        node.battery_pct = payload.battery_pct
    if payload.signal_rssi is not None:
        node.signal_rssi = payload.signal_rssi

    # Calculate rate of change for water level (delta in meters per 30 minutes)
    water_roc = 0.0
    if payload.water_level_m is not None:
        prev_record = (
            db.query(TelemetryRecord)
            .filter(TelemetryRecord.node_id == payload.node_id)
            .order_by(desc(TelemetryRecord.timestamp))
            .first()
        )
        if prev_record and prev_record.water_level_m is not None:
            time_diff = (datetime.utcnow() - prev_record.timestamp).total_seconds()
            if time_diff > 0:
                # Normalize rate to 30 minutes (1800 seconds)
                delta_h = payload.water_level_m - prev_record.water_level_m
                water_roc = round((delta_h / time_diff) * 1800.0, 2)

    # Save telemetry record
    record = TelemetryRecord(
        node_id=payload.node_id,
        timestamp=datetime.utcnow(),
        water_level_m=payload.water_level_m,
        water_rate_of_change=water_roc,
        temperature_c=payload.temperature_c,
        humidity_pct=payload.humidity_pct,
        wind_speed_kmh=payload.wind_speed_kmh,
        wind_direction_deg=payload.wind_direction_deg or 0.0,
        pm25=payload.pm25,
        pm10=payload.pm10,
        mesh_hops=payload.mesh_hops
    )
    db.add(record)
    db.commit()

    # --- Real-Time AI Predictive & Threshold Evaluation ---
    alerts_triggered = []

    # 1. Flood Assessment
    if payload.water_level_m is not None:
        flood_res = ai_engine.forecast_flood(payload.water_level_m, water_roc)
        if flood_res["is_flash_surge"]:
            alert = await alert_dispatcher.trigger_hazard_alert(
                db=db,
                hazard_type="FLOOD",
                severity="EMERGENCY",
                title=f"Extreme Flash Flood Surge - {node.name}",
                description=f"Rapid water rise of {water_roc:.2f}m in 30 mins! AI predicts river overflow in {flood_res['time_to_overflow_mins'] or 30} mins.",
                location_name=node.name,
                latitude=node.latitude,
                longitude=node.longitude,
                radius_km=4.5
            )
            alerts_triggered.append(alert.id)
        elif payload.water_level_m >= settings.FLOOD_CRITICAL:
            alert = await alert_dispatcher.trigger_hazard_alert(
                db=db,
                hazard_type="FLOOD",
                severity="CRITICAL",
                title=f"River Level Above Danger Mark ({payload.water_level_m:.2f}m)",
                description=f"Critical flood threshold breached at {node.name}.",
                location_name=node.name,
                latitude=node.latitude,
                longitude=node.longitude,
                radius_km=3.5
            )
            alerts_triggered.append(alert.id)

    # 2. Wildfire Assessment
    if payload.temperature_c and payload.humidity_pct and payload.wind_speed_kmh:
        fire_vector = ai_engine.calculate_wildfire_spread(
            lat=node.latitude,
            lon=node.longitude,
            temp_c=payload.temperature_c,
            humidity_pct=payload.humidity_pct,
            wind_speed_kmh=payload.wind_speed_kmh,
            wind_direction_deg=payload.wind_direction_deg or 0.0
        )
        if fire_vector.fire_danger_index >= 50:
            alert = await alert_dispatcher.trigger_hazard_alert(
                db=db,
                hazard_type="FIRE",
                severity="EMERGENCY",
                title=f"Extreme Wildfire Hazard - {node.name}",
                description=f"FFDI: {fire_vector.fire_danger_index} ({fire_vector.danger_category}). Wind propagating fire at {fire_vector.propagation_speed_kmh} km/h along bearing {fire_vector.bearing_degrees}°.",
                location_name=node.name,
                latitude=node.latitude,
                longitude=node.longitude,
                radius_km=6.0
            )
            alerts_triggered.append(alert.id)

    # 3. AQI Assessment
    if payload.pm25 is not None and payload.pm25 >= settings.AQI_SEVERE:
        alert = await alert_dispatcher.trigger_hazard_alert(
            db=db,
            hazard_type="POLLUTION",
            severity="CRITICAL",
            title=f"Hazardous Air Quality Spike - {node.name}",
            description=f"PM2.5 reached {payload.pm25:.1f} ug/m3. Issue health advisory for sensitive groups.",
            location_name=node.name,
            latitude=node.latitude,
            longitude=node.longitude,
            radius_km=5.0
        )
        alerts_triggered.append(alert.id)

    # Broadcast telemetry update over WebSockets to live UI
    await ws_manager.broadcast("TELEMETRY_UPDATE", {
        "node_id": node.id,
        "name": node.name,
        "water_level_m": payload.water_level_m,
        "water_rate_of_change": water_roc,
        "temperature_c": payload.temperature_c,
        "humidity_pct": payload.humidity_pct,
        "wind_speed_kmh": payload.wind_speed_kmh,
        "pm25": payload.pm25,
        "mesh_hops": payload.mesh_hops,
        "battery_pct": node.battery_pct,
        "status": node.status,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "status": "success",
        "node_id": node.id,
        "water_rate_of_change": water_roc,
        "alerts_triggered": alerts_triggered
    }

@router.get("/latest", response_model=List[dict])
def get_latest_telemetry(db: Session = Depends(get_db)):
    """Returns the latest reading for each active node."""
    nodes = db.query(SensorNode).all()
    results = []
    for node in nodes:
        latest = (
            db.query(TelemetryRecord)
            .filter(TelemetryRecord.node_id == node.id)
            .order_by(desc(TelemetryRecord.timestamp))
            .first()
        )
        results.append({
            "node_id": node.id,
            "name": node.name,
            "latitude": node.latitude,
            "longitude": node.longitude,
            "hazard_type": node.hazard_type,
            "status": node.status,
            "hop_count": node.hop_count,
            "battery_pct": node.battery_pct,
            "signal_rssi": node.signal_rssi,
            "is_gateway": node.is_gateway,
            "water_level_m": latest.water_level_m if latest else None,
            "water_rate_of_change": latest.water_rate_of_change if latest else 0.0,
            "temperature_c": latest.temperature_c if latest else None,
            "humidity_pct": latest.humidity_pct if latest else None,
            "wind_speed_kmh": latest.wind_speed_kmh if latest else None,
            "pm25": latest.pm25 if latest else None,
            "last_seen": node.last_seen.isoformat()
        })
    return results

@router.get("/history/{node_id}", response_model=List[TelemetryResponse])
def get_node_telemetry_history(node_id: str, limit: int = 30, db: Session = Depends(get_db)):
    """Fetches historical time-series data for a single node for frontend graphs."""
    records = (
        db.query(TelemetryRecord)
        .filter(TelemetryRecord.node_id == node_id)
        .order_by(desc(TelemetryRecord.timestamp))
        .limit(limit)
        .all()
    )
    return list(reversed(records))

@router.get("/ai-forecast/{node_id}", response_model=AIPredictionResponse)
def get_ai_forecast(node_id: str, db: Session = Depends(get_db)):
    """Generates real-time 3-hour predictive curves and vector calculations for a specific node."""
    node = db.query(SensorNode).filter(SensorNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    latest = (
        db.query(TelemetryRecord)
        .filter(TelemetryRecord.node_id == node_id)
        .order_by(desc(TelemetryRecord.timestamp))
        .first()
    )

    # Query recent historical water levels for ARIMA(2,1,1) fit
    history_records = (
        db.query(TelemetryRecord)
        .filter(TelemetryRecord.node_id == node_id)
        .order_by(desc(TelemetryRecord.timestamp))
        .limit(10)
        .all()
    )
    history_water = [r.water_level_m for r in reversed(history_records) if r.water_level_m is not None]

    current_water = latest.water_level_m if latest and latest.water_level_m is not None else 1.8
    current_roc = latest.water_rate_of_change if latest and latest.water_rate_of_change is not None else 0.1
    current_temp = latest.temperature_c if latest and latest.temperature_c is not None else 28.0
    current_hum = latest.humidity_pct if latest and latest.humidity_pct is not None else 50.0
    current_wind = latest.wind_speed_kmh if latest and latest.wind_speed_kmh is not None else 12.0
    current_pm25 = latest.pm25 if latest and latest.pm25 is not None else 45.0

    flood_analysis = ai_engine.forecast_flood(
        current_water_level=current_water,
        rate_of_change_30m=current_roc,
        history_values=history_water if len(history_water) >= 4 else None
    )
    fire_analysis = ai_engine.calculate_wildfire_spread(
        lat=node.latitude,
        lon=node.longitude,
        temp_c=current_temp,
        humidity_pct=current_hum,
        wind_speed_kmh=current_wind,
        wind_direction_deg=latest.wind_direction_deg if latest else 45.0
    )
    aqi_analysis = ai_engine.analyze_pollution_spike(current_pm25)

    summary = f"{flood_analysis['summary']} | Fire Risk: {fire_analysis.danger_category} | AQI: {aqi_analysis['severity']}"

    return AIPredictionResponse(
        node_id=node.id,
        hazard_type=node.hazard_type,
        timestamp=datetime.utcnow(),
        flood_forecast_3h=flood_analysis["forecast_points"],
        fire_spread_vector=fire_analysis,
        aqi_smog_window_hours=aqi_analysis["window_hours"],
        ai_summary=summary,
        arima_order=flood_analysis.get("arima_order", "ARIMA(2,1,1)"),
        arima_expected_baseline=flood_analysis.get("expected_baseline"),
        residual_error=flood_analysis.get("residual_error"),
        anomaly_z_score=flood_analysis.get("anomaly_z_score"),
        is_residual_anomaly=flood_analysis.get("is_anomaly", False),
        residual_status=flood_analysis.get("decision", "NORMAL")
    )
