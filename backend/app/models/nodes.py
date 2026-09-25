from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base, IS_SQLITE

if not IS_SQLITE:
    from geoalchemy2 import Geography
    LocationPoint = Geography(geometry_type="POINT", srid=4326, spatial_index=True)
else:
    LocationPoint = Text

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    hazard_type = Column(String(30), default="multi")  # flood, fire, air, multi
    location = Column(LocationPoint, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), default="normal")      # normal, warning, critical, offline
    battery_pct = Column(Float, default=100.0)
    signal_strength = Column(Float, default=-65.0)     # RSSI dBm
    mesh_level = Column(Integer, default=0)            # 0 = gateway sink
    parent_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)
    is_gateway = Column(Boolean, default=False)
    is_simulated = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    api_key_hash = Column(String(64), nullable=True)   # SHA-256 hex digest
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship("Node", remote_side=[id], backref="children")
    readings = relationship("Reading", back_populates="node", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="node", cascade="all, delete-orphan")
