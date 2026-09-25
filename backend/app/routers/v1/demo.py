import os
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.nodes import Node
from app.models.alerts import Alert
from app.models.readings import Reading
from app.schemas.v1_schemas import DemoTriggerRequest, DemoNetworkRequest
from app.websocket_manager import ws_manager

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

router = APIRouter(prefix="/demo", tags=["Demonstration & Sandbox Controls"])

# In-memory queue for simulating offline store-and-forward when a node network is cut
_node_outage_queues: Dict[str, list] = {}

def check_demo_mode():
    if not DEMO_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo controls are disabled in production mode (DEMO_MODE=false)"
        )

@router.post("/trigger", response_model=dict, dependencies=[Depends(check_demo_mode)])
async def trigger_demo_event(payload: DemoTriggerRequest, db: Session = Depends(get_db)):
    """Simulates a rapid hazard spike (flood, smoke, aqi) on a specific node."""
    target_code = str(payload.node_id)
    if target_code.isdigit():
        node = db.query(Node).filter(Node.id == int(target_code)).first()
    else:
        node = db.query(Node).filter(Node.code == target_code).first()

    if not node:
        # Fallback to Node 2 or Node 3
        node = db.query(Node).filter(Node.code == "NODE-02").first() or db.query(Node).first()

    now = datetime.utcnow()
    hazard_type = payload.type.lower()

    if hazard_type == "flood":
        node.status = "critical"
        reading = Reading(
            node_id=node.id,
            ts=now,
            water_level_cm=485.0,
            water_rate_cm_min=8.5,
            pm25=35.0,
            temperature_c=24.0,
            humidity=92.0,
            raw_bytes=2400,
            tx_bytes=128
        )
        db.add(reading)

        alert = Alert(
            node_id=node.id,
            hazard_type="flood",
            severity="critical",
            confidence=0.95,
            message=f"Extreme Flash Flood Surge on {node.name}",
            decided_on_device=True,
            decision_ms=38,
            reason="Water level rise > 8 cm/min (Surge rate 8.5 cm/min). Breached 4.0m danger mark.",
            node_timestamp=now,
            received_at=now,
            delivered_after_outage=False,
            status="open",
            ground_truth="unverified",
            latitude=node.latitude,
            longitude=node.longitude
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        await ws_manager.broadcast("alert", {
            "id": alert.id,
            "node_id": node.id,
            "node_code": node.code,
            "hazard_type": "flood",
            "severity": "critical",
            "confidence": alert.confidence,
            "message": alert.message,
            "decided_on_device": True,
            "decision_ms": alert.decision_ms,
            "reason": alert.reason,
            "node_timestamp": alert.node_timestamp.isoformat(),
            "received_at": alert.received_at.isoformat(),
            "delivered_after_outage": False,
            "status": "open",
            "ground_truth": "unverified",
            "latitude": alert.latitude,
            "longitude": alert.longitude
        })

    elif hazard_type == "smoke":
        node.status = "critical"
        reading = Reading(
            node_id=node.id,
            ts=now,
            water_level_cm=30.0,
            temperature_c=44.2,
            humidity=12.0,
            wind_speed=32.0,
            wind_dir=225.0,
            smoke_index=88.5,
            raw_bytes=2400,
            tx_bytes=128
        )
        db.add(reading)

        alert = Alert(
            node_id=node.id,
            hazard_type="fire",
            severity="critical",
            confidence=0.91,
            message=f"Dense Smoke & Thermal Anomaly on {node.name}",
            decided_on_device=True,
            decision_ms=42,
            reason="Smoke index reached 88.5; ambient temperature 44.2°C with 32 km/h wind.",
            node_timestamp=now,
            received_at=now,
            delivered_after_outage=False,
            status="open",
            ground_truth="unverified",
            latitude=node.latitude,
            longitude=node.longitude
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        await ws_manager.broadcast("alert", {
            "id": alert.id,
            "node_id": node.id,
            "node_code": node.code,
            "hazard_type": "fire",
            "severity": "critical",
            "confidence": alert.confidence,
            "message": alert.message,
            "decided_on_device": True,
            "decision_ms": alert.decision_ms,
            "reason": alert.reason,
            "node_timestamp": alert.node_timestamp.isoformat(),
            "received_at": alert.received_at.isoformat(),
            "delivered_after_outage": False,
            "status": "open",
            "ground_truth": "unverified",
            "latitude": alert.latitude,
            "longitude": alert.longitude
        })

    elif hazard_type == "aqi":
        node.status = "warning"
        reading = Reading(
            node_id=node.id,
            ts=now,
            pm25=348.0,
            pm10=490.0,
            temperature_c=19.5,
            humidity=75.0,
            smoke_index=45.0,
            raw_bytes=2400,
            tx_bytes=128
        )
        db.add(reading)

        alert = Alert(
            node_id=node.id,
            hazard_type="air",
            severity="warning",
            confidence=0.96,
            message=f"Severe PM2.5 Smog Advisory on {node.name}",
            decided_on_device=True,
            decision_ms=35,
            reason="PM2.5 concentration spiked to 348 ug/m3. Hazardous inversion window active.",
            node_timestamp=now,
            received_at=now,
            delivered_after_outage=False,
            status="open",
            ground_truth="unverified",
            latitude=node.latitude,
            longitude=node.longitude
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        await ws_manager.broadcast("alert", {
            "id": alert.id,
            "node_id": node.id,
            "node_code": node.code,
            "hazard_type": "air",
            "severity": "warning",
            "confidence": alert.confidence,
            "message": alert.message,
            "decided_on_device": True,
            "decision_ms": alert.decision_ms,
            "reason": alert.reason,
            "node_timestamp": alert.node_timestamp.isoformat(),
            "received_at": alert.received_at.isoformat(),
            "delivered_after_outage": False,
            "status": "open",
            "ground_truth": "unverified",
            "latitude": alert.latitude,
            "longitude": alert.longitude
        })

    # Broadcast updated node status
    await ws_manager.broadcast("node_status", {
        "node_id": node.id,
        "node_code": node.code,
        "status": node.status,
        "battery_pct": node.battery_pct,
        "signal_strength": node.signal_strength
    })

    return {
        "status": "success",
        "node_code": node.code,
        "event_type": payload.type,
        "message": f"Injected {payload.type} emergency on {node.name}"
    }

@router.post("/network", response_model=dict, dependencies=[Depends(check_demo_mode)])
async def control_node_network(payload: DemoNetworkRequest, db: Session = Depends(get_db)):
    """
    Simulates cutting or restoring network on a specific node.
    When cut: node turns offline/grey, alerts are queued locally.
    When restored: queued alerts flush into backend with original timestamps, marked 'delivered_after_outage'.
    """
    target_code = str(payload.node_id)
    if target_code.isdigit():
        node = db.query(Node).filter(Node.id == int(target_code)).first()
    else:
        node = db.query(Node).filter(Node.code == target_code).first()

    if not node:
        node = db.query(Node).filter(Node.code == "NODE-03").first() or db.query(Node).first()

    action = payload.action.lower()

    if action == "cut":
        node.status = "offline"
        # Create an outage queue for this node and buffer a simulated event that occurred during the outage
        outage_time = datetime.utcnow() - timedelta(minutes=4)
        _node_outage_queues[node.code] = [
            {
                "hazard_type": "flood",
                "severity": "critical",
                "confidence": 0.93,
                "message": f"Store-and-Forward Surge Alert on {node.name}",
                "decision_ms": 40,
                "reason": "Water rise > 9 cm/min detected during network blackout",
                "node_timestamp": outage_time
            }
        ]
        db.commit()

        await ws_manager.broadcast("node_status", {
            "node_id": node.id,
            "node_code": node.code,
            "status": "offline"
        })

        return {
            "status": "cut",
            "node_code": node.code,
            "message": f"Network severed for {node.name}. Node is now OFFLINE. Alerts will queue in on-chip flash buffer."
        }

    elif action == "restore":
        node.status = "normal"
        node.last_seen = datetime.utcnow()
        db.commit()

        # Flush queued alerts
        flushed_count = 0
        now = datetime.utcnow()
        if node.code in _node_outage_queues:
            for item in _node_outage_queues[node.code]:
                orig_ts = item["node_timestamp"]
                alert = Alert(
                    node_id=node.id,
                    hazard_type=item["hazard_type"],
                    severity=item["severity"],
                    confidence=item["confidence"],
                    message=item["message"],
                    decided_on_device=True,
                    decision_ms=item["decision_ms"],
                    reason=item["reason"],
                    node_timestamp=orig_ts,
                    received_at=now,
                    delivered_after_outage=True,
                    status="open",
                    ground_truth="unverified",
                    latitude=node.latitude,
                    longitude=node.longitude
                )
                db.add(alert)
                db.flush()
                flushed_count += 1

                # Broadcast to dashboard with delivered_after_outage = True
                await ws_manager.broadcast("alert", {
                    "id": alert.id,
                    "node_id": node.id,
                    "node_code": node.code,
                    "hazard_type": alert.hazard_type,
                    "severity": alert.severity,
                    "confidence": alert.confidence,
                    "message": alert.message,
                    "decided_on_device": True,
                    "decision_ms": alert.decision_ms,
                    "reason": alert.reason,
                    "node_timestamp": alert.node_timestamp.isoformat(),
                    "received_at": alert.received_at.isoformat(),
                    "delivered_after_outage": True,
                    "status": "open",
                    "ground_truth": "unverified",
                    "latitude": alert.latitude,
                    "longitude": alert.longitude
                })

            del _node_outage_queues[node.code]
            db.commit()

        await ws_manager.broadcast("node_status", {
            "node_id": node.id,
            "node_code": node.code,
            "status": "normal"
        })

        return {
            "status": "restored",
            "node_code": node.code,
            "flushed_alerts": flushed_count,
            "message": f"Network restored on {node.name}. Flushed {flushed_count} queued alerts with 'Delivered after outage' badge!"
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown network action: {payload.action}")
