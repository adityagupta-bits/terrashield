from sqlalchemy import Column, Integer, String, Text
from app.db.session import Base, IS_SQLITE

if not IS_SQLITE:
    from geoalchemy2 import Geography
    LocationPolygon = Geography(geometry_type="POLYGON", srid=4326, spatial_index=True)
else:
    LocationPolygon = Text

class HazardZone(Base):
    __tablename__ = "hazard_zones"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    hazard_type = Column(String(30), nullable=False)   # flood, fire, air, multi
    geom = Column(LocationPolygon, nullable=True)
    geom_geojson = Column(Text, nullable=True)         # GeoJSON Polygon string for fast API delivery
    risk_level = Column(String(20), default="medium")  # low, medium, high, critical
