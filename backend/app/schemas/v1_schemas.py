from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Auth Schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    token: str
    role: str
    email: str

from pydantic import BaseModel, Field, ConfigDict, model_validator

# Ingestion Schemas
class ReadingIngest(BaseModel):
    node_code: str = ""
    ts: Optional[datetime] = None
    water_level_cm: Optional[float] = None
    water_rate_cm_min: Optional[float] = 0.0
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_dir: Optional[float] = 0.0
    smoke_index: Optional[float] = None
    battery_pct: Optional[float] = None
    rssi: Optional[float] = None
    raw_bytes: Optional[int] = 2400
    tx_bytes: Optional[int] = 128

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("node_code") and data.get("node_id"):
                data["node_code"] = data["node_id"]
            if data.get("water_level_cm") is None and data.get("water_level_m") is not None:
                data["water_level_cm"] = round(data["water_level_m"] * 100.0, 2)
            if data.get("humidity") is None and data.get("humidity_pct") is not None:
                data["humidity"] = data["humidity_pct"]
            if data.get("ts") is None and data.get("timestamp") is not None:
                data["ts"] = data["timestamp"]
            if (data.get("water_rate_cm_min") is None or data.get("water_rate_cm_min") == 0.0) and data.get("water_rate_of_change") is not None:
                data["water_rate_cm_min"] = round(data["water_rate_of_change"] * 100.0, 2)
        return data

class AlertIngest(BaseModel):
    node_code: str
    node_timestamp: datetime
    hazard_type: str = "flood"  # flood, fire, air
    severity: str = "critical"  # warning, critical
    confidence: float = 0.92
    decision_ms: int = 40
    reason: Optional[str] = "Threshold breached on-device"
    readings_summary: Optional[Dict[str, Any]] = None

class BatchIngest(BaseModel):
    node_code: str
    items: List[Dict[str, Any]]

# Node Schemas
class NodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    name: str
    hazard_type: str
    latitude: float
    longitude: float
    status: str
    battery_pct: float
    signal_strength: float
    mesh_level: int
    parent_node_id: Optional[int] = None
    parent_code: Optional[str] = None
    is_gateway: bool
    is_simulated: bool
    last_seen: datetime

# Alert Schemas
class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    node_id: Optional[int] = None
    node_code: Optional[str] = None
    hazard_type: str
    severity: str
    confidence: float
    message: str
    decided_on_device: bool
    decision_ms: int
    reason: Optional[str] = None
    node_timestamp: datetime
    received_at: datetime
    delivered_after_outage: bool
    status: str
    ground_truth: str
    latitude: float
    longitude: float

class AlertStatusUpdate(BaseModel):
    status: str  # acknowledged, resolved, dispatched

# Broadcast Schemas
class BroadcastRequest(BaseModel):
    lat: float
    lng: float
    radius_km: float = Field(default=5.0, ge=1.0, le=50.0)
    template_id: str  # flood_warning, fire_warning, aqi_advisory, evacuate_now, all_clear

class BroadcastPreviewResponse(BaseModel):
    recipients_count: int
    radius_km: float

class BroadcastResponse(BaseModel):
    broadcast_id: int
    recipients_count: int
    template_id: str
    sent_at: datetime

# Contact Schemas
class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str
    phone: str
    district: str
    capacity: Optional[int] = None
    occupancy: Optional[int] = None
    latitude: float
    longitude: float
    distance_km: Optional[float] = None

# Weather Schemas
class WeatherCurrentResponse(BaseModel):
    region: str
    temp_c: float
    humidity: float
    rainfall_mm: float
    wind_kmh: float
    risk_badge: str  # Low, Medium, High
    ts: datetime

class WeatherForecastPoint(BaseModel):
    time: str
    temp_c: float
    rainfall_mm: float
    risk_level: str
    predicted: bool = True

class WeatherForecastResponse(BaseModel):
    region: str
    points: List[WeatherForecastPoint]
    note: str = "Forecast based on past weather data"

# Multi-Hazard Risk Forecaster Schemas
class RiskAssessmentItem(BaseModel):
    risk_type: str
    triggered: bool
    score: float
    reasons: List[str]

class DailyWeatherProjection(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    humidity: float
    precipitation: float
    pressure: float
    wind_speed: float

class MultiHazardRiskResponse(BaseModel):
    region: str
    coordinates: Dict[str, float]
    horizon_days: int
    overall_severity: str
    max_risk_score: float
    triggered_hazards: List[str]
    dates: List[str]
    daily_projections: List[DailyWeatherProjection]
    risks: Dict[str, RiskAssessmentItem]
    model_metadata: Optional[Dict[str, Any]] = None


# News Schemas
class NewsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    region: str
    title: str
    summary: str
    source: str
    published_at: datetime

# Stats Schemas
class StatsResponse(BaseModel):
    nodes_online: int
    total_nodes: int
    open_alerts: int
    bytes_raw_local: int
    bytes_transmitted: int
    alerts_sent_whatsapp_today: int
    last_alert_time: Optional[str] = None

# Citizen Schemas
class ShelterDetail(BaseModel):
    id: int
    name: str
    distance_km: float
    capacity: int
    occupancy: int
    available_spots: int
    phone: str

class CitizenStatusResponse(BaseModel):
    status: str  # safe, caution, evacuate
    severity: str
    message: str
    hazard_type: str
    nearest_shelters: List[ShelterDetail]

# Demo Schemas
class DemoTriggerRequest(BaseModel):
    node_id: Union[int, str]
    type: str  # flood, smoke, aqi

class DemoNetworkRequest(BaseModel):
    node_id: Union[int, str]
    action: str  # cut, restore
