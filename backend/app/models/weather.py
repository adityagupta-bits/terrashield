from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.session import Base

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    region = Column(String(100), default="Rishikesh-Garhwal Catchment")
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    temp_c = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    rainfall_mm = Column(Float, default=0.0)
    wind_kmh = Column(Float, nullable=True)

class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    region = Column(String(100), default="Rishikesh-Garhwal Catchment")
    forecast_time = Column(DateTime, nullable=False, index=True)
    temp_c = Column(Float, nullable=False)
    rainfall_mm = Column(Float, default=0.0)
    risk_level = Column(String(20), default="low")      # low, medium, high
    predicted_at = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50), default="v1.0-gb")
