"""
Central configuration for Weather Risk Forecaster integrated into TERRA SHIELD.
Tunable thresholds for flood, drought, and fire risk assessment.
"""

import os

# OpenWeather API (optional, can be passed via environment or settings)
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

# Default coordinates: Brahmaputra & Kopili River Basin, Assam (16 June Incident)
DEFAULT_LAT = 26.1850
DEFAULT_LON = 91.7500

ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"
ONECALL_TIMEMACHINE_URL = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
ONECALL_DAY_SUMMARY_URL = "https://api.openweathermap.org/data/3.0/onecall/day_summary"

HISTORY_DAYS_TO_FETCH = 45
FORECAST_HORIZON_DAYS = 7

# Target meteorological variables modeled via ARIMA
TARGET_VARIABLES = ["temp_max", "temp_min", "humidity", "precipitation", "pressure", "wind_speed"]

# Multi-hazard risk thresholds calibrated for catchment & foothill terrains
THRESHOLDS = {
    "flood": {
        "cumulative_precip_mm": 100.0,      # total forecasted rain over horizon
        "single_day_precip_mm": 50.0,       # any single day exceeding this
        "min_humidity_pct": 80.0,
    },
    "drought": {
        "max_cumulative_precip_mm": 2.0,
        "min_avg_temp_c": 30.0,
        "max_avg_humidity_pct": 35.0,
    },
    "fire": {
        "min_avg_temp_c": 32.0,
        "max_avg_humidity_pct": 30.0,
        "min_avg_wind_speed_ms": 4.0,
        "max_cumulative_precip_mm": 1.0,
    },
}
