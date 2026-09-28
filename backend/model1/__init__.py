"""
TERRA SHIELD - Model1: ARIMA Weather Risk Forecaster Package
Forecasts key meteorological variables using per-variable ARIMA,
and calculates composite multi-hazard risk scores (Flood, Drought, Wildfire).
"""

from .config import (
    DEFAULT_LAT,
    DEFAULT_LON,
    FORECAST_HORIZON_DAYS,
    TARGET_VARIABLES,
    THRESHOLDS
)
from .arima_model import (
    fit_and_forecast_series,
    forecast_all_variables,
    forecasts_to_dataframe,
    ForecastResult
)
from .risk_assessment import (
    assess_flood_risk,
    assess_drought_risk,
    assess_fire_risk,
    assess_all,
    RiskAssessment
)
from .data_loader import (
    load_history_csv,
    generate_synthetic_history,
    clean_and_fill
)

__all__ = [
    "DEFAULT_LAT",
    "DEFAULT_LON",
    "FORECAST_HORIZON_DAYS",
    "TARGET_VARIABLES",
    "THRESHOLDS",
    "fit_and_forecast_series",
    "forecast_all_variables",
    "forecasts_to_dataframe",
    "ForecastResult",
    "assess_flood_risk",
    "assess_drought_risk",
    "assess_fire_risk",
    "assess_all",
    "RiskAssessment",
    "load_history_csv",
    "generate_synthetic_history",
    "clean_and_fill",
]
