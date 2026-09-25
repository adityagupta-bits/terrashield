import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "TERRA SHIELD"
    PROJECT_ID: str = "SIH26178"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./terrashield.db")
    
    # Default Region Center (Rishikesh / Ganga Basin, Uttarakhand)
    DEFAULT_LAT: float = 30.0869
    DEFAULT_LNG: float = 78.2676
    DEFAULT_REGION_NAME: str = "Rishikesh-Garhwal Catchment"
    
    # Flood Thresholds (meters)
    FLOOD_NORMAL_MAX: float = 2.5
    FLOOD_CAUTION_MAX: float = 4.0
    FLOOD_CRITICAL: float = 4.0
    FLOOD_FLASH_RATE_THRESHOLD: float = 1.5  # meters rise in 30 minutes
    
    # Fire Risk Thresholds
    FIRE_TEMP_CRITICAL: float = 42.0       # Celsius
    FIRE_HUMIDITY_CRITICAL: float = 15.0    # Percentage
    FIRE_WIND_CRITICAL: float = 25.0        # km/h
    
    # Air Quality Thresholds (PM2.5 in ug/m3 or AQI)
    AQI_MODERATE_MAX: float = 100.0
    AQI_POOR_MAX: float = 200.0
    AQI_SEVERE: float = 300.0
    
    # Twilio / WhatsApp Settings
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "mock_sid")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "mock_token")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    MOCK_WHATSAPP: bool = True  # Allows offline/local presentation simulation

settings = Settings()
