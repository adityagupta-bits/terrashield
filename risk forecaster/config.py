"""
Central configuration: API access, location, and the threshold rules used to
turn forecasted weather variables into flood / drought / fire-risk labels.

Tune THRESHOLDS to your climate zone. The defaults are generic starting
points, not scientifically calibrated values for any specific region.
"""

import os

# --- OpenWeather API ---------------------------------------------------
# Get a free key at https://openweathermap.org/api
# Put it in a .env file as OPENWEATHER_API_KEY=xxxx or export it in your shell.
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

# Location to model (default: example coordinates, override via CLI args)
DEFAULT_LAT = 17.3850   # Hyderabad, IN as an example
DEFAULT_LON = 78.4867

# One Call 3.0 endpoints
ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"
ONECALL_TIMEMACHINE_URL = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
ONECALL_DAY_SUMMARY_URL = "https://api.openweathermap.org/data/3.0/onecall/day_summary"

# --- Data / modeling ------------------------------------------------------
# How many days of history to try to pull from the API day-summary endpoint.
# NOTE: OpenWeather's free/paid tiers limit how far back you can query.
# For serious ARIMA training, prefer feeding in a longer historical CSV
# (see data_loader.load_history_csv) sourced from NASA POWER, NOAA, IMD, etc.
HISTORY_DAYS_TO_FETCH = 45

# How many days ahead to forecast with ARIMA
FORECAST_HORIZON_DAYS = 7

# Variables we model independently with their own ARIMA process
TARGET_VARIABLES = ["temp_max", "temp_min", "humidity", "precipitation", "pressure", "wind_speed"]

# --- Risk thresholds --------------------------------------------------
# These are simple, explainable rules applied to the ARIMA forecasts.
# Replace with values appropriate to your region / season, or replace this
# whole layer with a trained classifier if you have labeled historical
# flood/drought/fire events to fit against.
THRESHOLDS = {
    "flood": {
        # Flag flood risk if forecasted rainfall over the horizon is high
        # AND humidity stays elevated (saturated ground / air).
        "cumulative_precip_mm": 100.0,      # total forecasted rain over horizon
        "single_day_precip_mm": 50.0,       # any single day exceeding this
        "min_humidity_pct": 80.0,
    },
    "drought": {
        # Flag drought risk if forecasted rainfall is near zero for the
        # whole horizon and humidity/temperature indicate high evaporation.
        "max_cumulative_precip_mm": 2.0,
        "min_avg_temp_c": 30.0,
        "max_avg_humidity_pct": 35.0,
    },
    "fire": {
        # Simplified fire-weather rule: hot, dry, and windy with no rain.
        "min_avg_temp_c": 32.0,
        "max_avg_humidity_pct": 30.0,
        "min_avg_wind_speed_ms": 4.0,
        "max_cumulative_precip_mm": 1.0,
    },
}
