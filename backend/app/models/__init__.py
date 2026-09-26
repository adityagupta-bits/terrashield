from app.db.session import Base
from app.models.nodes import Node
from app.models.readings import Reading
from app.models.alerts import Alert
from app.models.hazard_zones import HazardZone
from app.models.contacts import Contact
from app.models.subscribers import Subscriber
from app.models.whatsapp import WhatsAppMessage, BroadcastLog
from app.models.weather import WeatherObservation, WeatherForecast
from app.models.news import NewsFlash
from app.models.users import User
from app.models.mesh import MeshLink

# Backward compatibility models
from app.models_legacy import (
    SensorNode,
    TelemetryRecord,
    IncidentAlert,
    WhatsAppVerification,
    SafeShelter
)

__all__ = [
    "Base",
    "Node",
    "Reading",
    "Alert",
    "HazardZone",
    "Contact",
    "Subscriber",
    "WhatsAppMessage",
    "BroadcastLog",
    "WeatherObservation",
    "WeatherForecast",
    "NewsFlash",
    "User",
    "MeshLink",
    "SensorNode",
    "TelemetryRecord",
    "IncidentAlert",
    "WhatsAppVerification",
    "SafeShelter"
]
