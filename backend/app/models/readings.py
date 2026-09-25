from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), index=True, nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    water_level_cm = Column(Float, nullable=True)
    water_rate_cm_min = Column(Float, default=0.0)
    pm25 = Column(Float, nullable=True)
    pm10 = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_dir = Column(Float, default=0.0)
    smoke_index = Column(Float, nullable=True)
    raw_bytes = Column(Integer, default=2400)
    tx_bytes = Column(Integer, default=128)
    raw_json = Column(Text, nullable=True)

    node = relationship("Node", back_populates="readings")
