import math
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.contacts import Contact
from app.schemas.v1_schemas import ContactResponse

router = APIRouter(prefix="/contacts", tags=["Emergency Contacts & Shelters"])

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

@router.get("", response_model=List[ContactResponse])
def get_contacts(
    category: Optional[str] = None,
    near: Optional[str] = Query(None, description="Comma-separated lat,lng for distance sorting"),
    db: Session = Depends(get_db)
):
    """Returns contacts, rescue units, shelters, and NGOs. Sorts by nearest if near=lat,lng provided."""
    query = db.query(Contact)
    if category:
        query = query.filter(Contact.category == category)

    contacts = query.all()

    near_lat, near_lng = None, None
    if near:
        try:
            parts = near.split(",")
            near_lat = float(parts[0].strip())
            near_lng = float(parts[1].strip())
        except Exception:
            near_lat, near_lng = None, None

    results = []
    for c in contacts:
        dist = None
        if near_lat is not None and near_lng is not None:
            dist = round(haversine(near_lat, near_lng, c.latitude, c.longitude), 2)

        results.append(
            ContactResponse(
                id=c.id,
                name=c.name,
                category=c.category,
                phone=c.phone,
                district=c.district,
                capacity=c.capacity,
                occupancy=c.occupancy,
                latitude=c.latitude,
                longitude=c.longitude,
                distance_km=dist
            )
        )

    if near_lat is not None:
        results.sort(key=lambda x: x.distance_km if x.distance_km is not None else 9999.0)

    return results
