from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base, IS_SQLITE

if not IS_SQLITE:
    from geoalchemy2 import Geography
    LocationPoint = Geography(geometry_type="POINT", srid=4326, spatial_index=True)
else:
    LocationPoint = Text

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), index=True, nullable=True)
    hazard_type = Column(String(30), nullable=False)   # flood, fire, air, multi
    severity = Column(String(20), nullable=False)      # warning, critical
    confidence = Column(Float, default=0.90)
    message = Column(String(255), nullable=False)
    decided_on_device = Column(Boolean, default=False)
    decision_ms = Column(Integer, default=40)
    reason = Column(Text, nullable=True)
    node_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    received_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    delivered_after_outage = Column(Boolean, default=False)
    status = Column(String(20), default="open")        # open, acknowledged, resolved, dispatched
    ground_truth = Column(String(20), default="unverified")  # unverified, confirmed, denied
    location = Column(LocationPoint, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    node = relationship("Node", back_populates="alerts")
    messages = relationship("WhatsAppMessage", back_populates="alert")
