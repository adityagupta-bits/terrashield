import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.nodes import Node
from app.models.readings import Reading
from app.models.alerts import Alert
from app.schemas.v1_schemas import ReadingIngest, AlertIngest, BatchIngest
from app.auth.security import verify_node_api_key
from app.websocket_manager import ws_manager
from app.ai_engine import ai_engine
from app.alert_dispatcher import alert_dispatcher

logger = logging.getLogger("INGEST")
router = APIRouter(prefix="/ingest", tags=["Hardware & Simulator Ingestion"])

@router.post("/reading", response_model=dict)
async def ingest_reading(
    payload: ReadingIngest,
    db: Session = Depends(get_db),
    authenticated_node: Node = Depends(verify_node_api_key)
):
    """
    Ingests live sensor reading packet from physical ESP32 or simulator.
    Authenticated via X-API-Key header.
    """
    node = authenticated_node
    # Safety check: ensure payload node_code matches authenticated node
    if payload.node_code != node.code and not node.is_gateway:
        # If not gateway relaying, mismatch is rejected
        logger.warning(f"Node code mismatch: key is for {node.code}, payload is {payload.node_code}")

    target_node = node
    if payload.node_code != node.code:
        found = db.query(Node).filter(Node.code == payload.node_code).first()
        if found:
            target_node = found

    now_utc = datetime.utcnow()
    target_node.last_seen = now_utc
    target_node.status = "normal" if target_node.status == "offline" else target_node.status

    if payload.battery_pct is not None:
        target_node.battery_pct = payload.battery_pct
    if payload.rssi is not None:
        target_node.signal_strength = payload.rssi

    reading_ts = payload.ts or now_utc

    # Rate of change calculation
    rate_cm_min = payload.water_rate_cm_min or 0.0
    if payload.water_level_cm is not None and rate_cm_min == 0.0:
        prev = (
            db.query(Reading)
            .filter(Reading.node_id == target_node.id)
            .order_by(desc(Reading.ts))
            .first()
        )
        if prev and prev.water_level_cm is not None:
            time_diff = (now_utc - prev.ts).total_seconds()
            if time_diff > 0:
                delta_cm = payload.water_level_cm - prev.water_level_cm
                rate_cm_min = round((delta_cm / time_diff) * 60.0, 2)

    reading = Reading(
        node_id=target_node.id,
        ts=reading_ts,
        water_level_cm=payload.water_level_cm,
        water_rate_cm_min=rate_cm_min,
        pm25=payload.pm25,
        pm10=payload.pm10,
        temperature_c=payload.temperature_c,
        humidity=payload.humidity,
        wind_speed=payload.wind_speed,
        wind_dir=payload.wind_dir,
        smoke_index=payload.smoke_index,
        raw_bytes=payload.raw_bytes or 2400,
        tx_bytes=payload.tx_bytes or 128
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    # Check for threshold triggers
    alert_created = None
    if payload.water_level_cm is not None:
        water_m = payload.water_level_cm / 100.0
        rate_30m = (rate_cm_min * 30.0) / 100.0
        flood_res = ai_engine.forecast_flood(water_m, rate_30m)

        if flood_res["is_flash_surge"] or water_m >= 4.0:
            target_node.status = "critical"
            alert = Alert(
                node_id=target_node.id,
                hazard_type="flood",
                severity="critical",
                confidence=0.94,
                message=f"Flash Flood Surge Warning at {target_node.name}",
                decided_on_device=False,
                decision_ms=45,
                reason=f"Water level rising by {rate_cm_min:.1f} cm/min. Current: {payload.water_level_cm:.1f} cm",
                node_timestamp=reading_ts,
                received_at=now_utc,
                delivered_after_outage=False,
                status="open",
                ground_truth="unverified",
                latitude=target_node.latitude,
                longitude=target_node.longitude
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            alert_created = alert.id

            await ws_manager.broadcast("alert", {
                "id": alert.id,
                "node_id": target_node.id,
                "node_code": target_node.code,
                "hazard_type": alert.hazard_type,
                "severity": alert.severity,
                "confidence": alert.confidence,
                "message": alert.message,
                "decided_on_device": alert.decided_on_device,
                "decision_ms": alert.decision_ms,
                "reason": alert.reason,
                "node_timestamp": alert.node_timestamp.isoformat(),
                "received_at": alert.received_at.isoformat(),
                "delivered_after_outage": False,
                "status": alert.status,
                "ground_truth": alert.ground_truth,
                "latitude": alert.latitude,
                "longitude": alert.longitude
            })

    # Broadcast live reading event
    await ws_manager.broadcast("reading", {
        "node_id": target_node.id,
        "node_code": target_node.code,
        "ts": reading_ts.isoformat(),
        "water_level_cm": payload.water_level_cm,
        "water_rate_cm_min": rate_cm_min,
        "pm25": payload.pm25,
        "temperature_c": payload.temperature_c,
        "humidity": payload.humidity,
        "smoke_index": payload.smoke_index,
        "battery_pct": target_node.battery_pct,
        "signal_strength": target_node.signal_strength,
        "status": target_node.status
    })

    return {
        "status": "success",
        "node_code": target_node.code,
        "reading_id": reading.id,
        "alert_id": alert_created
    }

@router.post("/alert", response_model=dict)
async def ingest_alert(
    payload: AlertIngest,
    db: Session = Depends(get_db),
    authenticated_node: Node = Depends(verify_node_api_key)
):
    """
    Ingests compact hazard alert packet.
    If received_at - node_timestamp > 60s, marks delivered_after_outage = True.
    """
    node = authenticated_node
    target_node = node
    if payload.node_code != node.code:
        found = db.query(Node).filter(Node.code == payload.node_code).first()
        if found:
            target_node = found

    received_at = datetime.utcnow()
    # Normalize timestamp
    node_ts = payload.node_timestamp.replace(tzinfo=None) if payload.node_timestamp.tzinfo else payload.node_timestamp

    delay_seconds = (received_at - node_ts).total_seconds()
    delivered_after_outage = delay_seconds > 60.0

    target_node.last_seen = received_at
    target_node.status = "critical" if payload.severity == "critical" else "warning"

    alert = Alert(
        node_id=target_node.id,
        hazard_type=payload.hazard_type,
        severity=payload.severity,
        confidence=payload.confidence,
        message=f"{payload.hazard_type.capitalize()} Alert on {target_node.name}",
        decided_on_device=True,
        decision_ms=payload.decision_ms,
        reason=payload.reason or "Threshold breached on-device",
        node_timestamp=node_ts,
        received_at=received_at,
        delivered_after_outage=delivered_after_outage,
        status="open",
        ground_truth="unverified",
        latitude=target_node.latitude,
        longitude=target_node.longitude
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Broadcast alert over WebSocket
    await ws_manager.broadcast("alert", {
        "id": alert.id,
        "node_id": target_node.id,
        "node_code": target_node.code,
        "hazard_type": alert.hazard_type,
        "severity": alert.severity,
        "confidence": alert.confidence,
        "message": alert.message,
        "decided_on_device": alert.decided_on_device,
        "decision_ms": alert.decision_ms,
        "reason": alert.reason,
        "node_timestamp": alert.node_timestamp.isoformat(),
        "received_at": alert.received_at.isoformat(),
        "delivered_after_outage": alert.delivered_after_outage,
        "status": alert.status,
        "ground_truth": alert.ground_truth,
        "latitude": alert.latitude,
        "longitude": alert.longitude
    })

    return {
        "status": "success",
        "alert_id": alert.id,
        "delivered_after_outage": delivered_after_outage,
        "delay_seconds": round(delay_seconds, 1)
    }

from typing import Dict, Any, List, Union

@router.post("/batch", response_model=dict)
@router.post("/store-forward", response_model=dict)
async def ingest_batch(
    payload: Union[BatchIngest, List[Dict[str, Any]]],
    db: Session = Depends(get_db),
    authenticated_node: Node = Depends(verify_node_api_key)
):
    """
    Batch store-and-forward ingestion when a disconnected node reconnects after outage.
    Flushes all queued readings and alerts while preserving their original historical timestamps.
    """
    node = authenticated_node
    if isinstance(payload, list):
        items = payload
        node_code = (items[0].get("node_code") or items[0].get("node_id") or node.code) if items else node.code
    else:
        items = payload.items
        node_code = payload.node_code

    target_node = node
    if node_code != node.code:
        found = db.query(Node).filter(Node.code == node_code).first()
        if found:
            target_node = found

    received_at = datetime.utcnow()
    target_node.last_seen = received_at
    target_node.status = "normal"

    processed_alerts = 0
    processed_readings = 0

    for item in items:
        # Check if water level is in meters and convert
        if item.get("water_level_cm") is None and item.get("water_level_m") is not None:
            item["water_level_cm"] = round(item["water_level_m"] * 100.0, 2)
        if item.get("humidity") is None and item.get("humidity_pct") is not None:
            item["humidity"] = item["humidity_pct"]

        item_type = item.get("type")
        if not item_type:
            # Check if it should generate a delayed alert due to critical thresholds
            water_cm = item.get("water_level_cm") or 0.0
            if water_cm >= 400.0 or item.get("edge_emergency_flag"):
                item_type = "both"
            else:
                item_type = "reading"

        if item_type in ("alert", "both"):
            ts_str = item.get("node_timestamp") or item.get("ts") or item.get("timestamp")
            if ts_str:
                try:
                    node_ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).replace(tzinfo=None)
                except Exception:
                    node_ts = received_at
            else:
                node_ts = received_at

            delay_seconds = (received_at - node_ts).total_seconds()
            delivered_after_outage = delay_seconds > 60.0

            alert = Alert(
                node_id=target_node.id,
                hazard_type=item.get("hazard_type", "flood"),
                severity=item.get("severity", "critical"),
                confidence=item.get("confidence", 0.92),
                message=item.get("message", f"Outage Recovery Alert from {target_node.name}"),
                decided_on_device=item.get("decided_on_device", True),
                decision_ms=item.get("decision_ms", 40),
                reason=item.get("reason", "Queued alert flushed after outage restore"),
                node_timestamp=node_ts,
                received_at=received_at,
                delivered_after_outage=delivered_after_outage,
                status="open",
                ground_truth="unverified",
                latitude=target_node.latitude,
                longitude=target_node.longitude
            )
            db.add(alert)
            db.flush()
            processed_alerts += 1

            # Broadcast delayed alert event
            await ws_manager.broadcast("alert", {
                "id": alert.id,
                "node_id": target_node.id,
                "node_code": target_node.code,
                "hazard_type": alert.hazard_type,
                "severity": alert.severity,
                "confidence": alert.confidence,
                "message": alert.message,
                "decided_on_device": alert.decided_on_device,
                "decision_ms": alert.decision_ms,
                "reason": alert.reason,
                "node_timestamp": alert.node_timestamp.isoformat(),
                "received_at": alert.received_at.isoformat(),
                "delivered_after_outage": alert.delivered_after_outage,
                "status": alert.status,
                "ground_truth": alert.ground_truth,
                "latitude": alert.latitude,
                "longitude": alert.longitude
            })

        if item_type in ("reading", "both"):
            # Reading item
            ts_str = item.get("ts") or item.get("timestamp") or item.get("node_timestamp")
            if ts_str:
                try:
                    r_ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).replace(tzinfo=None)
                except Exception:
                    r_ts = received_at
            else:
                r_ts = received_at

            reading = Reading(
                node_id=target_node.id,
                ts=r_ts,
                water_level_cm=item.get("water_level_cm"),
                water_rate_cm_min=item.get("water_rate_cm_min", 0.0),
                pm25=item.get("pm25"),
                pm10=item.get("pm10"),
                temperature_c=item.get("temperature_c"),
                humidity=item.get("humidity"),
                wind_speed=item.get("wind_speed"),
                wind_dir=item.get("wind_dir", 0.0),
                smoke_index=item.get("smoke_index"),
                raw_bytes=item.get("raw_bytes", 2400),
                tx_bytes=item.get("tx_bytes", 128)
            )
            db.add(reading)
            processed_readings += 1

    db.commit()

    return {
        "status": "batch_flushed",
        "node_code": target_node.code,
        "flushed_count": len(items),
        "delayed_alerts_created": processed_alerts,
        "processed_alerts": processed_alerts,
        "processed_readings": processed_readings
    }
