"""
Per-variable ARIMA forecasting.

Each weather variable (temp_max, humidity, precipitation, ...) is forecast
independently with its own ARIMA(p,d,q) model. Order is chosen automatically
with a small grid search on AIC (a lightweight stand-in for auto_arima, so
we don't need the pmdarima package).
"""

from __future__ import annotations

import itertools
import warnings
from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings("ignore")  # statsmodels is noisy about convergence warnings


@dataclass
class ForecastResult:
    variable: str
    order: tuple
    forecast: pd.Series          # point forecasts, indexed by future date
    conf_int_lower: pd.Series
    conf_int_upper: pd.Series
    aic: float


def _grid_search_order(series: pd.Series, p_range=range(0, 4), d_range=range(0, 2), q_range=range(0, 4)):
    """Pick the (p,d,q) with the lowest AIC over a small grid. Falls back to (1,1,1) if all fail."""
    best_aic = np.inf
    best_order = (1, 1, 1)
    for p, d, q in itertools.product(p_range, d_range, q_range):
        if p == 0 and q == 0:
            continue
        try:
            model = ARIMA(series, order=(p, d, q))
            fit = model.fit()
            if fit.aic < best_aic:
                best_aic = fit.aic
                best_order = (p, d, q)
        except Exception:
            continue
    return best_order, best_aic


def fit_and_forecast(series: pd.Series, horizon: int, variable_name: str) -> ForecastResult:
    """
    Fit an ARIMA model to `series` (a clean, gap-free daily time series) and
    forecast `horizon` days ahead with 95% confidence intervals.
    """
    series = series.dropna()
    if len(series) < 14:
        raise ValueError(
            f"Only {len(series)} data points for '{variable_name}' - ARIMA needs "
            "considerably more history (ideally 60+ daily points) to fit reliably."
        )

    order, aic = _grid_search_order(series)
    model = ARIMA(series, order=order)
    fit = model.fit()

    forecast_res = fit.get_forecast(steps=horizon)
    mean_fc = forecast_res.predicted_mean
    ci = forecast_res.conf_int(alpha=0.05)

    future_index = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
    mean_fc.index = future_index
    ci.index = future_index

    return ForecastResult(
        variable=variable_name,
        order=order,
        forecast=mean_fc,
        conf_int_lower=ci.iloc[:, 0],
        conf_int_upper=ci.iloc[:, 1],
        aic=aic,
    )


def forecast_all_variables(history_df: pd.DataFrame, horizon: int) -> Dict[str, ForecastResult]:
    """Run fit_and_forecast for every column in history_df."""
    results = {}
    for col in history_df.columns:
        try:
            results[col] = fit_and_forecast(history_df[col], horizon, col)
        except Exception as e:
            print(f"  [warn] could not model '{col}': {e}")
    return results


def forecasts_to_dataframe(results: Dict[str, ForecastResult]) -> pd.DataFrame:
    """Collapse {variable: ForecastResult} into one tidy DataFrame of point forecasts."""
    data = {name: res.forecast for name, res in results.items()}
    return pd.DataFrame(data)
