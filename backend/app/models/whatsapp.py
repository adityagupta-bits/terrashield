from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base, IS_SQLITE

if not IS_SQLITE:
    from geoalchemy2 import Geography
    LocationPoint = Geography(geometry_type="POINT", srid=4326, spatial_index=True)
else:
    LocationPoint = Text = String

class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=True)
    direction = Column(String(10), default="outbound") # inbound, outbound
    body = Column(Text, nullable=False)
    parsed_intent = Column(String(50), nullable=True)
    verdict = Column(String(30), nullable=True)        # CONFIRMED, DENIED, UNCERTAIN
    confidence = Column(Float, default=0.0)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)

    subscriber = relationship("Subscriber", back_populates="messages")
    alert = relationship("Alert", back_populates="messages")

class BroadcastLog(Base):
    __tablename__ = "broadcast_log"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    center = Column(LocationPoint, nullable=True)
    center_lat = Column(Float, nullable=False)
    center_lng = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False)
    template_id = Column(String(50), nullable=False)
    recipients_count = Column(Integer, default=0)
    sent_by = Column(String(100), default="Authority Command Center")
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
