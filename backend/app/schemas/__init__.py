from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Telemetry Schemas
class TelemetryIngest(BaseModel):
    node_id: str
    water_level_m: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    mesh_hops: int = 0
    parent_node_id: Optional[str] = None
    battery_pct: Optional[float] = None
    signal_rssi: Optional[float] = None

class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    node_id: str
    timestamp: datetime
    water_level_m: Optional[float]
    water_rate_of_change: Optional[float]
    temperature_c: Optional[float]
    humidity_pct: Optional[float]
    wind_speed_kmh: Optional[float]
    wind_direction_deg: Optional[float]
    pm25: Optional[float]
    pm10: Optional[float]
    mesh_hops: int

# Node Schemas
class SensorNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    hazard_type: str
    latitude: float
    longitude: float
    status: str
    parent_node_id: Optional[str]
    hop_count: int
    battery_pct: float
    signal_rssi: float
    is_gateway: bool
    last_seen: datetime

# Alert Schemas
class IncidentAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hazard_type: str
    severity: str
    title: str
    description: str
    location_name: str
    latitude: float
    longitude: float
    radius_km: float
    timestamp: datetime
    is_active: bool
    verified_by_human: bool
    verification_source: Optional[str]
    evacuation_triggered: bool
    ndrf_dispatched: bool

class AlertActionRequest(BaseModel):
    action: str  # "EVACUATE", "DISPATCH_NDRF", "RESOLVE"

# WhatsApp Bot Schemas
class WhatsAppIncomingWebhook(BaseModel):
    From: str = Field(..., description="Sender phone number with whatsapp: prefix")
    Body: str = Field(..., description="Message text from Sarpanch")
    Latitude: Optional[float] = None
    Longitude: Optional[float] = None
    MediaUrl0: Optional[str] = None

class WhatsAppVerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    incident_id: int
    sarpanch_name: str
    phone_number: str
    query_sent: str
    query_language: str
    response_received: Optional[str]
    verification_status: str
    nlp_confidence: float
    timestamp: datetime

from pydantic import BaseModel, ConfigDict, model_validator

# Shelter Schemas
class SafeShelterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    shelter_type: Optional[str] = "SHELTER"
    latitude: float
    longitude: float
    capacity: Optional[int] = 200
    current_occupancy: Optional[int] = 35
    contact_number: Optional[str] = "1070"
    is_open: Optional[bool] = True

    @model_validator(mode="before")
    @classmethod
    def map_contact_fields(cls, data: Any) -> Any:
        if hasattr(data, "phone") and not hasattr(data, "contact_number"):
            return {
                "id": data.id,
                "name": data.name,
                "shelter_type": getattr(data, "category", "SHELTER") or "SHELTER",
                "latitude": data.latitude,
                "longitude": data.longitude,
                "capacity": getattr(data, "capacity", 200) or 200,
                "current_occupancy": 35,
                "contact_number": getattr(data, "phone", "1070") or "1070",
                "is_open": getattr(data, "is_active", True)
            }
        return data

# AI Forecast Schemas
class FloodForecastPoint(BaseModel):
    time_offset_hours: float
    predicted_water_level_m: float
    risk_level: str  # NORMAL, CAUTION, CRITICAL

class FireSpreadVector(BaseModel):
    fire_danger_index: float  # 0 to 100
    danger_category: str      # Low, Moderate, Very High, Extreme
    propagation_speed_kmh: float
    bearing_degrees: float
    cone_polygon_coords: List[List[float]]  # [[lat, lng], ...]

class AIPredictionResponse(BaseModel):
    node_id: str
    hazard_type: str
    timestamp: datetime
    flood_forecast_3h: List[FloodForecastPoint] = []
    fire_spread_vector: Optional[FireSpreadVector] = None
    aqi_smog_window_hours: Optional[float] = None
    ai_summary: str
    # ARIMA (p, d, q) & Residual Anomaly Scoring Extensions
    arima_order: str = "ARIMA(2,1,1)"
    arima_expected_baseline: Optional[float] = None
    residual_error: Optional[float] = None
    anomaly_z_score: Optional[float] = None
    is_residual_anomaly: Optional[bool] = False
    residual_status: Optional[str] = "NORMAL"

# Simulation Schemas
class SimulationTriggerRequest(BaseModel):
    scenario: str  # "FLASH_FLOOD", "WILDFIRE", "POLLUTION_SPIKE", "CELLULAR_BLACKOUT", "RESET"
    target_node_id: Optional[str] = None
    intensity: float = 1.0

# Mesh Topology Schemas
class MeshTopologyLink(BaseModel):
    source: str
    target: str
    hop_level: int
    signal_rssi: float

class MeshTopologyResponse(BaseModel):
    network_mode: str  # "HYBRID_CELLULAR" or "DECENTRALIZED_MESH_BLACKOUT"
    nodes: List[SensorNodeResponse]
    links: List[MeshTopologyLink]
    active_gateways: int
    total_mesh_hops: int

from app.schemas import v1_schemas
