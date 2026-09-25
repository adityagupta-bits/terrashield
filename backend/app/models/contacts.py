from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base, IS_SQLITE

if not IS_SQLITE:
    from geoalchemy2 import Geography
    LocationPoint = Geography(geometry_type="POINT", srid=4326, spatial_index=True)
else:
    LocationPoint = Text = String

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(30), nullable=False)      # authority, rescue, shelter, ngo, helpline
    phone = Column(String(30), nullable=False)
    district = Column(String(50), default="Dehradun / Tehri Garhwal")
    capacity = Column(Integer, nullable=True)          # for shelters
    occupancy = Column(Integer, nullable=True)         # current occupancy
    location = Column(LocationPoint, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
