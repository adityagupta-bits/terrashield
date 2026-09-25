import math
from app.db.session import engine, SessionLocal, Base, get_db

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in km between two points on earth."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def is_within_radius(target_lat: float, target_lon: float, center_lat: float, center_lon: float, radius_km: float) -> bool:
    return haversine_distance_km(target_lat, target_lon, center_lat, center_lon) <= radius_km
