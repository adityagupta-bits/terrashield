import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.hazard_zones import HazardZone

router = APIRouter(prefix="/zones", tags=["Hazard Zones"])

@router.get("", response_model=dict)
def get_hazard_zones(db: Session = Depends(get_db)):
    """Returns all active hazard zones as a standard GeoJSON FeatureCollection."""
    zones = db.query(HazardZone).all()
    features = []

    for z in zones:
        geometry = None
        if z.geom_geojson:
            try:
                geometry = json.loads(z.geom_geojson)
            except Exception:
                geometry = None

        if geometry:
            features.append({
                "type": "Feature",
                "id": z.id,
                "properties": {
                    "id": z.id,
                    "name": z.name,
                    "hazard_type": z.hazard_type,
                    "risk_level": z.risk_level
                },
                "geometry": geometry
            })

    return {
        "type": "FeatureCollection",
        "features": features
    }
