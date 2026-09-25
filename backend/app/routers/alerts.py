from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import IncidentAlert, SafeShelter
from app.schemas import IncidentAlertResponse, AlertActionRequest, SafeShelterResponse
from app.alert_dispatcher import alert_dispatcher
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/alerts", tags=["Disaster Alerts & Incident Management"])

@router.get("", response_model=List[IncidentAlertResponse])
def get_alerts(active_only: bool = False, db: Session = Depends(get_db)):
    """Fetches disaster incident alerts."""
    query = db.query(IncidentAlert)
    if active_only:
        query = query.filter(IncidentAlert.is_active == True)
    return query.order_by(desc(IncidentAlert.timestamp)).limit(50).all()

@router.post("/{alert_id}/action", response_model=IncidentAlertResponse)
async def take_alert_action(alert_id: int, request: AlertActionRequest, db: Session = Depends(get_db)):
    """Authorities action on active alert: Trigger Evacuation, Dispatch NDRF, or Resolve."""
    alert = db.query(IncidentAlert).filter(IncidentAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Incident alert not found")

    if request.action == "EVACUATE":
        alert.evacuation_triggered = True
        alert.severity = "EMERGENCY"
    elif request.action == "DISPATCH_NDRF":
        alert.ndrf_dispatched = True
    elif request.action == "RESOLVE":
        alert.is_active = False
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action {request.action}")

    db.commit()
    db.refresh(alert)

    # Broadcast updated alert status to all connected dashboards
    await ws_manager.broadcast("ALERT_STATUS_CHANGED", {
        "alert_id": alert.id,
        "action": request.action,
        "evacuation_triggered": alert.evacuation_triggered,
        "ndrf_dispatched": alert.ndrf_dispatched,
        "is_active": alert.is_active
    })

    return alert

@router.get("/shelters", response_model=List[SafeShelterResponse])
def get_safe_shelters(db: Session = Depends(get_db)):
    """Lists safe evacuation shelters, relief camps, and emergency hospitals."""
    shelters = db.query(SafeShelter).filter(SafeShelter.category.in_(["SHELTER", "RESCUE", "MEDICAL"])).all()
    if not shelters:
        shelters = db.query(SafeShelter).all()
    return shelters

@router.get("/citizen-check", response_model=dict)
def check_citizen_status(
    lat: float = Query(..., description="Citizen latitude"),
    lon: float = Query(..., description="Citizen longitude"),
    db: Session = Depends(get_db)
):
    """
    Checks citizen's real-time GPS coordinates against active hazard geofences.
    Returns status (SAFE / CAUTION / DANGER), advisory text, and nearest evacuation shelters.
    """
    return alert_dispatcher.check_citizen_risk_zone(db, lat, lon)
