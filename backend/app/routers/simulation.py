from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SensorNode, TelemetryRecord, IncidentAlert, WhatsAppVerification
from app.schemas import SimulationTriggerRequest
from app.alert_dispatcher import alert_dispatcher
from app.mesh_manager import mesh_manager
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/simulation", tags=["Hackathon Simulation & Demo Sandbox"])

@router.get("/scenarios")
def get_available_scenarios():
    return [
        {
            "id": "FLASH_FLOOD",
            "name": "Extreme Flash Flood Surge",
            "description": "Simulates cloudburst upstream in Shivpuri-Byasi canyon. River surges +1.9m in 30 mins, triggering predictive AI flash flood alert and automated WhatsApp message to village Sarpanch.",
            "target_default": "NODE-03"
        },
        {
            "id": "WILDFIRE",
            "name": "Chilla Forest Wildfire Hotspot",
            "description": "Simulates 44°C heatwave, 11% humidity, and 30 km/h south-westerly wind at Rajaji-Chilla range. Triggers McArthur FFDI calculations and dynamic directional fire spread cone.",
            "target_default": "NODE-07"
        },
        {
            "id": "POLLUTION_SPIKE",
            "name": "Severe AQI Smog Emergency",
            "description": "Simulates localized agricultural residue burning & thermal inversion causing PM2.5 to spike to 345 ug/m3. Triggers automated public health advisory.",
            "target_default": "NODE-13"
        },
        {
            "id": "CELLULAR_BLACKOUT",
            "name": "Cellular Tower Blackout & Mesh Failover",
            "description": "Simulates total cellular infrastructure outage. Primary GSM gateway fails; nodes dynamically reroute packets across decentralized multi-hop LoRa mesh to emergency backup sink.",
            "target_default": "ALL"
        },
        {
            "id": "RESET",
            "name": "Reset to Safe Baseline",
            "description": "Restores all river levels to 1.6m normal, clears active disaster alerts, and restores normal hybrid cellular connectivity.",
            "target_default": "ALL"
        }
    ]

@router.post("/trigger", response_model=dict)
async def trigger_simulation_scenario(req: SimulationTriggerRequest, db: Session = Depends(get_db)):
    """Triggers an instantaneous multi-hazard disaster simulation scenario for live presentation."""
    scenario = req.scenario.upper()

    if scenario == "FLASH_FLOOD":
        target_id = req.target_node_id or "NODE-03"
        node = db.query(SensorNode).filter(SensorNode.id == target_id).first()
        if not node:
            node = db.query(SensorNode).filter(SensorNode.hazard_type == "flood").first()
        
        # Inject extreme water surge
        record = TelemetryRecord(
            node_id=node.id,
            timestamp=datetime.utcnow(),
            water_level_m=4.85,
            water_rate_of_change=1.92,
            temperature_c=24.0,
            humidity_pct=92.0,
            wind_speed_kmh=18.0,
            mesh_hops=node.hop_count
        )
        db.add(record)
        db.commit()

        # Trigger emergency alert
        alert = await alert_dispatcher.trigger_hazard_alert(
            db=db,
            hazard_type="FLOOD",
            severity="EMERGENCY",
            title=f"Flash Flood Surge Warning - {node.name}",
            description=f"Rapid upstream surge of 1.92m in 30 minutes! River level at 4.85m (Breaching 4.0m critical mark). AI model predicts overflow within 35 minutes.",
            location_name=node.name,
            latitude=node.latitude,
            longitude=node.longitude,
            radius_km=4.5
        )

        return {
            "status": "triggered",
            "scenario": "FLASH_FLOOD",
            "node_id": node.id,
            "alert_id": alert.id,
            "message": f"Flash flood injected at {node.name}. WhatsApp Sarpanch verification dispatched!"
        }

    elif scenario == "WILDFIRE":
        target_id = req.target_node_id or "NODE-07"
        node = db.query(SensorNode).filter(SensorNode.id == target_id).first()
        if not node:
            node = db.query(SensorNode).filter(SensorNode.hazard_type == "fire").first()

        record = TelemetryRecord(
            node_id=node.id,
            timestamp=datetime.utcnow(),
            water_level_m=0.3,
            temperature_c=44.2,
            humidity_pct=11.5,
            wind_speed_kmh=31.0,
            wind_direction_deg=225.0, # South-West wind
            mesh_hops=node.hop_count
        )
        db.add(record)
        db.commit()

        alert = await alert_dispatcher.trigger_hazard_alert(
            db=db,
            hazard_type="FIRE",
            severity="EMERGENCY",
            title=f"Critical Wildfire Spread Alert - {node.name}",
            description="Extreme McArthur FFDI index (Extreme 68.4). 31 km/h wind pushing active front north-east towards inhabited forest fringe.",
            location_name=node.name,
            latitude=node.latitude,
            longitude=node.longitude,
            radius_km=5.5
        )

        return {
            "status": "triggered",
            "scenario": "WILDFIRE",
            "node_id": node.id,
            "alert_id": alert.id,
            "message": f"Wildfire outbreak injected at {node.name}. Directional spread vector calculated!"
        }

    elif scenario == "POLLUTION_SPIKE":
        target_id = req.target_node_id or "NODE-13"
        node = db.query(SensorNode).filter(SensorNode.id == target_id).first()
        if not node:
            node = db.query(SensorNode).filter(SensorNode.hazard_type == "pollution").first()

        record = TelemetryRecord(
            node_id=node.id,
            timestamp=datetime.utcnow(),
            pm25=348.0,
            pm10=495.0,
            temperature_c=19.5,
            humidity_pct=78.0,
            wind_speed_kmh=4.0,
            mesh_hops=node.hop_count
        )
        db.add(record)
        db.commit()

        alert = await alert_dispatcher.trigger_hazard_alert(
            db=db,
            hazard_type="POLLUTION",
            severity="CRITICAL",
            title=f"Severe Toxic Smog Surge - {node.name}",
            description="PM2.5 spiked to 348 ug/m3. Thermal inversion trapped hazardous particulates. Issue health advisory.",
            location_name=node.name,
            latitude=node.latitude,
            longitude=node.longitude,
            radius_km=4.0
        )

        return {
            "status": "triggered",
            "scenario": "POLLUTION_SPIKE",
            "node_id": node.id,
            "alert_id": alert.id,
            "message": f"AQI smog spike injected at {node.name}."
        }

    elif scenario == "CELLULAR_BLACKOUT":
        status = mesh_manager.toggle_cellular_blackout(db, not mesh_manager.cellular_blackout)
        await ws_manager.broadcast("NETWORK_STATE_CHANGE", {
            "cellular_blackout": status,
            "mode": "DECENTRALIZED_MESH_BLACKOUT" if status else "HYBRID_CELLULAR"
        })
        return {
            "status": "toggled",
            "cellular_blackout": status,
            "mode": "DECENTRALIZED_MESH_BLACKOUT" if status else "HYBRID_CELLULAR",
            "message": "Switched to decentralized offline mesh mode!" if status else "Restored cellular uplink."
        }

    elif scenario == "RESET":
        # Reset nodes to safe values
        mesh_manager.toggle_cellular_blackout(db, False)
        
        # Deactivate all active alerts
        alerts = db.query(IncidentAlert).filter(IncidentAlert.is_active == True).all()
        for a in alerts:
            a.is_active = False
        db.commit()

        # Insert normal baseline telemetry for all nodes
        nodes = db.query(SensorNode).all()
        for n in nodes:
            rec = TelemetryRecord(
                node_id=n.id,
                timestamp=datetime.utcnow(),
                water_level_m=1.65,
                water_rate_of_change=0.02,
                temperature_c=26.5,
                humidity_pct=55.0,
                wind_speed_kmh=9.0,
                wind_direction_deg=45.0,
                pm25=42.0,
                pm10=70.0,
                mesh_hops=n.hop_count
            )
            db.add(rec)
        db.commit()

        await ws_manager.broadcast("SIMULATION_RESET", {"message": "All sensor values reset to baseline."})

        return {"status": "reset", "message": "All parameters normalized to safe baseline."}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown scenario {req.scenario}")
