from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base, IS_SQLITE

if not IS_SQLITE:
    from geoalchemy2 import Geography
    LocationPoint = Geography(geometry_type="POINT", srid=4326, spatial_index=True)
else:
    LocationPoint = Text = String

class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    whatsapp_number = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(30), default="citizen")       # citizen, sarpanch, councillor
    language = Column(String(10), default="hi")        # en, hi, te, ta
    location = Column(LocationPoint, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, default=5.0)
    village = Column(String(100), nullable=False)
    opted_in_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("WhatsAppMessage", back_populates="subscriber", cascade="all, delete-orphan")
