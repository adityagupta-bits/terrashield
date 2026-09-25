import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models import IncidentAlert, SafeShelter, SensorNode
from app.database import is_within_radius, haversine_distance_km
from app.websocket_manager import ws_manager
from app.whatsapp_bot import whatsapp_bot

logger = logging.getLogger(__name__)

class AlertDispatcher:
    """Dispatches multi-tier disaster warnings to authorities, citizens, and vernacular channels."""

    async def trigger_hazard_alert(
        self,
        db: Session,
        hazard_type: str,
        severity: str,
        title: str,
        description: str,
        location_name: str,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0
    ) -> IncidentAlert:
        """Creates an incident alert, logs it, prompts WhatsApp verification, and broadcasts via WebSockets."""
        alert = IncidentAlert(
            hazard_type=hazard_type,
            severity=severity,
            title=title,
            description=description,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            is_active=True,
            verified_by_human=False,
            evacuation_triggered=(severity == "EMERGENCY"),
            ndrf_dispatched=False
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        # Dispatch automatic WhatsApp verification to local Sarpanch
        try:
            whatsapp_bot.dispatch_verification_request(
                db=db,
                incident=alert,
                sarpanch_name=f"Sarpanch of {location_name}",
                phone_number="+919876543210",
                lang="hi"
            )
        except Exception as e:
            logger.error(f"Failed to dispatch WhatsApp verification: {e}")

        # Broadcast real-time incident event to dashboard via WebSocket
        await ws_manager.broadcast("INCIDENT_ALERT", {
            "id": alert.id,
            "hazard_type": alert.hazard_type,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "location_name": alert.location_name,
            "latitude": alert.latitude,
            "longitude": alert.longitude,
            "radius_km": alert.radius_km,
            "timestamp": alert.timestamp.isoformat(),
            "evacuation_triggered": alert.evacuation_triggered
        })

        return alert

    def find_nearest_shelters(
        self,
        db: Session,
        user_lat: float,
        user_lon: float,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Returns the nearest open evacuation shelters with distances."""
        shelters = db.query(SafeShelter).filter(SafeShelter.is_open == True).all()
        results = []
        for s in shelters:
            dist = haversine_distance_km(user_lat, user_lon, s.latitude, s.longitude)
            results.append({
                "id": s.id,
                "name": s.name,
                "type": s.shelter_type,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "distance_km": round(dist, 2),
                "capacity": s.capacity,
                "available_spots": s.capacity - s.current_occupancy,
                "contact": s.contact_number
            })
        
        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]

    def check_citizen_risk_zone(
        self,
        db: Session,
        citizen_lat: float,
        citizen_lon: float
    ) -> Dict[str, Any]:
        """Checks if a citizen GPS coordinate falls inside any active hazard geofence."""
        active_alerts = db.query(IncidentAlert).filter(IncidentAlert.is_active == True).all()
        nearest_alert = None
        min_dist = 999999.0

        for alert in active_alerts:
            dist = haversine_distance_km(citizen_lat, citizen_lon, alert.latitude, alert.longitude)
            if dist <= alert.radius_km:
                nearest_alert = alert
                break
            elif dist < min_dist:
                min_dist = dist

        nearest_shelters = self.find_nearest_shelters(db, citizen_lat, citizen_lon, limit=2)

        if nearest_alert:
            return {
                "status": "DANGER" if nearest_alert.severity in ["CRITICAL", "EMERGENCY"] else "CAUTION",
                "hazard_type": nearest_alert.hazard_type,
                "severity": nearest_alert.severity,
                "incident_title": nearest_alert.title,
                "advisory": (
                    "EVACUATE IMMEDIATELY to designated high-ground shelter!"
                    if nearest_alert.evacuation_triggered or nearest_alert.severity == "EMERGENCY"
                    else "High risk alert in your sector. Stay tuned to emergency broadcasts."
                ),
                "nearest_shelters": nearest_shelters
            }
        else:
            return {
                "status": "SAFE",
                "hazard_type": "NONE",
                "severity": "NORMAL",
                "incident_title": "Normal Zone",
                "advisory": "No active hazard warnings in your immediate 5km radius.",
                "nearest_shelters": nearest_shelters
            }

alert_dispatcher = AlertDispatcher()
