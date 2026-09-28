"""
TERRA SHIELD Weather Risk Forecaster Package.
Provides multi-variable ARIMA forecasting and explainable multi-hazard risk assessment
(Flood, Drought, Wildfire).
"""

from app.risk_forecaster.arima_model import (
    fit_and_forecast,
    forecast_all_variables,
    forecasts_to_dataframe,
    ForecastResult,
)
from app.risk_forecaster.risk_assessment import (
    assess_all,
    assess_flood_risk,
    assess_drought_risk,
    assess_fire_risk,
    RiskAssessment,
)
from app.risk_forecaster.data_loader import (
    load_history_csv,
    generate_synthetic_history,
    fetch_history_from_api,
    clean_and_fill,
)
from app.risk_forecaster import config

__all__ = [
    "fit_and_forecast",
    "forecast_all_variables",
    "forecasts_to_dataframe",
    "ForecastResult",
    "assess_all",
    "assess_flood_risk",
    "assess_drought_risk",
    "assess_fire_risk",
    "RiskAssessment",
    "load_history_csv",
    "generate_synthetic_history",
    "fetch_history_from_api",
    "clean_and_fill",
    "config",
]
