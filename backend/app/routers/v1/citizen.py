import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.alerts import Alert
from app.models.contacts import Contact
from app.schemas.v1_schemas import CitizenStatusResponse, ShelterDetail

router = APIRouter(prefix="/citizen", tags=["Citizen Advisory & Safety Status"])

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

@router.get("/status", response_model=CitizenStatusResponse)
def get_citizen_status(
    lat: float = Query(...),
    lng: float = Query(...),
    lang: str = Query("en"),
    db: Session = Depends(get_db)
):
    """
    Checks citizen GPS coordinates against active disaster hazard geofences.
    Returns Safe, Caution, or Emergency Evacuation Warning status with nearest shelters.
    """
    active_alerts = db.query(Alert).filter(Alert.status.in_(["open", "acknowledged", "dispatched"])).all()

    nearest_hazard_alert = None
    min_hazard_dist = 999999.0

    for a in active_alerts:
        dist = haversine(lat, lng, a.latitude, a.longitude)
        if dist <= 5.0:  # 5km impact radius
            nearest_hazard_alert = a
            min_hazard_dist = dist
            break
        elif dist < min_hazard_dist:
            min_hazard_dist = dist

    # Fetch shelters
    shelters = db.query(Contact).filter(Contact.category == "shelter").all()
    shelter_details = []
    for s in shelters:
        s_dist = round(haversine(lat, lng, s.latitude, s.longitude), 2)
        cap = s.capacity or 400
        occ = s.occupancy or 20
        shelter_details.append(
            ShelterDetail(
                id=s.id,
                name=s.name,
                distance_km=s_dist,
                capacity=cap,
                occupancy=occ,
                available_spots=max(0, cap - occ),
                phone=s.phone
            )
        )

    shelter_details.sort(key=lambda x: x.distance_km)
    top_shelters = shelter_details[:3]

    if nearest_hazard_alert:
        if nearest_hazard_alert.severity == "critical" or nearest_hazard_alert.status == "dispatched":
            status_str = "evacuate"
            severity = "critical"
            msg = (
                "खतरा! तुरंत ऊंचे स्थान और निकटतम आश्रय केंद्र की ओर जाएं!"
                if lang == "hi"
                else "EMERGENCY EVACUATION WARNING: Move immediately to high-ground shelter!"
            )
        else:
            status_str = "caution"
            severity = "warning"
            msg = (
                "सावधानी: आपके क्षेत्र में जलस्तर/खतरा बढ़ रहा है। आपातकालीन घोषणाओं का ध्यान रखें।"
                if lang == "hi"
                else "CAUTION: Rising hazard levels in your sector. Stay prepared to evacuate."
            )
        hazard_type = nearest_hazard_alert.hazard_type
    else:
        status_str = "safe"
        severity = "normal"
        msg = (
            "आपका क्षेत्र सुरक्षित है। 5 किमी के दायरे में कोई सक्रिय आपदा चेतावनी नहीं है।"
            if lang == "hi"
            else "YOUR ZONE IS SAFE: No active hazard alerts detected within 5 km."
        )
        hazard_type = "none"

    return CitizenStatusResponse(
        status=status_str,
        severity=severity,
        message=msg,
        hazard_type=hazard_type,
        nearest_shelters=top_shelters
    )
