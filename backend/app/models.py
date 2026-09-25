from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class SensorNode(Base):
    __tablename__ = "sensor_nodes"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    hazard_type = Column(String(50), default="multi")  # flood, fire, pollution, multi
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(30), default="ONLINE")      # ONLINE, MESH_RELAY, OFFLINE, GATEWAY
    parent_node_id = Column(String(50), nullable=True) # ID of next hop in mesh
    hop_count = Column(Integer, default=0)             # 0 = direct gateway
    battery_pct = Column(Float, default=100.0)
    signal_rssi = Column(Float, default=-65.0)         # dBm
    is_gateway = Column(Boolean, default=False)
    last_seen = Column(DateTime, default=datetime.utcnow)

    telemetry = relationship("TelemetryRecord", back_populates="node", cascade="all, delete-orphan")

class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), ForeignKey("sensor_nodes.id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Flood parameters
    water_level_m = Column(Float, nullable=True)
    water_rate_of_change = Column(Float, default=0.0)  # m per 30 mins
    
    # Fire & Atmospheric parameters
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    wind_speed_kmh = Column(Float, nullable=True)
    wind_direction_deg = Column(Float, default=0.0)
    
    # Air Quality parameters
    pm25 = Column(Float, nullable=True)
    pm10 = Column(Float, nullable=True)
    
    # Network Hop metadata
    mesh_hops = Column(Integer, default=0)
    raw_payload = Column(Text, nullable=True)

    node = relationship("SensorNode", back_populates="telemetry")

class IncidentAlert(Base):
    __tablename__ = "incident_alerts"

    id = Column(Integer, primary_key=True, index=True)
    hazard_type = Column(String(30), nullable=False)   # FLOOD, FIRE, POLLUTION
    severity = Column(String(30), nullable=False)      # CAUTION, CRITICAL, EMERGENCY
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    location_name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, default=5.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Human-as-a-sensor verification
    verified_by_human = Column(Boolean, default=False)
    verification_source = Column(String(100), nullable=True)
    
    # Action states
    evacuation_triggered = Column(Boolean, default=False)
    ndrf_dispatched = Column(Boolean, default=False)

    verifications = relationship("WhatsAppVerification", back_populates="incident")

class WhatsAppVerification(Base):
    __tablename__ = "whatsapp_verifications"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incident_alerts.id"), index=True)
    sarpanch_name = Column(String(100), nullable=False)
    phone_number = Column(String(30), nullable=False)
    query_sent = Column(Text, nullable=False)
    query_language = Column(String(10), default="hi")  # hi, te, ta, en
    response_received = Column(Text, nullable=True)
    verification_status = Column(String(30), default="PENDING") # PENDING, CONFIRMED, FALSE_ALARM
    nlp_confidence = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    incident = relationship("IncidentAlert", back_populates="verifications")

class SafeShelter(Base):
    __tablename__ = "safe_shelters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    shelter_type = Column(String(50), default="SHELTER")  # SHELTER, HOSPITAL, RELIEF_CAMP
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, default=500)
    current_occupancy = Column(Integer, default=0)
    contact_number = Column(String(30), default="+91 1070")
    is_open = Column(Boolean, default=True)
