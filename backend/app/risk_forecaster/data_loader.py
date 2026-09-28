"""
Data loading and synthesis layer for TERRA SHIELD Weather Risk Forecaster.
Supports CSV ingestion, synthetic catchment histories, and OpenWeather API integration.
"""

from __future__ import annotations

import os
import datetime as dt
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests

from app.risk_forecaster import config


def load_history_csv(path: Optional[str] = None, date_col: str = "date") -> pd.DataFrame:
    """
    Load historical weather data from a CSV. If path is None, looks for sample_data_2years.csv
    in the workspace or default search paths.
    """
    if path is None or not os.path.exists(path):
        # Check standard locations
        search_paths = [
            Path(__file__).parent.parent.parent / "data" / "assam_weather_2years.csv",
            Path(__file__).parent.parent.parent.parent / "risk forecaster" / "sample_data_2years.csv",
            Path(__file__).parent / "data" / "sample_data_2years.csv",
            Path("risk forecaster/sample_data_2years.csv"),
            Path("sample_data_2years.csv"),
        ]
        found = None
        for p in search_paths:
            if p.exists():
                found = str(p)
                break
        if found:
            path = found
        else:
            # Fall back to synthetic data if CSV not found
            return generate_synthetic_history(days=365)

    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if date_col not in df.columns:
        raise ValueError(f"CSV must contain a '{date_col}' column.")

    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col).sort_index()

    for col in config.TARGET_VARIABLES:
        if col not in df.columns:
            df[col] = np.nan

    return df[config.TARGET_VARIABLES]


def generate_synthetic_history(days: int = 365, seed: int = 42) -> pd.DataFrame:
    """
    Generates realistic historical daily weather for Himalayan/foothill catchments
    with monsoon surge spikes and dry-season heat.
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=dt.date.today() - dt.timedelta(days=1), periods=days, freq="D")

    day_of_year = dates.dayofyear.values
    seasonal_temp = 25 + 9 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    temp_max = seasonal_temp + rng.normal(3, 1.5, days)
    temp_min = seasonal_temp - 7 + rng.normal(0, 1.2, days)

    # Monsoon precipitation cycle
    monsoon = np.clip(np.sin(2 * np.pi * (day_of_year - 170) / 365), 0, None) ** 2
    precipitation = np.clip(rng.exponential(2 + 28 * monsoon, days) - 2, 0, None)

    humidity = np.clip(45 + 38 * monsoon + rng.normal(0, 5, days), 15, 100)
    pressure = 1013 + rng.normal(0, 4, days) - 4 * monsoon
    wind_speed = np.clip(3.5 + rng.normal(0, 1.5, days) + 2.5 * monsoon, 0.5, None)

    df = pd.DataFrame(
        {
            "temp_max": np.round(temp_max, 1),
            "temp_min": np.round(temp_min, 1),
            "humidity": np.round(humidity, 1),
            "precipitation": np.round(precipitation, 1),
            "pressure": np.round(pressure, 1),
            "wind_speed": np.round(wind_speed, 1),
        },
        index=dates,
    )
    return df


def fetch_history_from_api(
    lat: float,
    lon: float,
    api_key: Optional[str] = None,
    days: int = config.HISTORY_DAYS_TO_FETCH,
    request_delay_sec: float = 0.5,
) -> pd.DataFrame:
    """Fetches daily summary histories from OpenWeather if key is configured."""
    key = api_key or config.OPENWEATHER_API_KEY
    if not key:
        return generate_synthetic_history(days=days)

    records = []
    today = dt.date.today()

    for i in range(days, 0, -1):
        day = today - dt.timedelta(days=i)
        params = {
            "lat": lat,
            "lon": lon,
            "date": day.isoformat(),
            "appid": key,
            "units": "metric",
        }
        try:
            resp = requests.get(config.ONECALL_DAY_SUMMARY_URL, params=params, timeout=10)
            if resp.status_code == 200:
                d = resp.json()
                records.append({
                    "date": day,
                    "temp_max": d.get("temperature", {}).get("max", 28.0),
                    "temp_min": d.get("temperature", {}).get("min", 18.0),
                    "humidity": d.get("humidity", {}).get("afternoon", 60.0),
                    "precipitation": d.get("precipitation", {}).get("total", 0.0),
                    "pressure": d.get("pressure", {}).get("afternoon", 1013.0),
                    "wind_speed": d.get("wind", {}).get("max", {}).get("speed", 4.0),
                })
        except Exception:
            continue

    if not records:
        return generate_synthetic_history(days=days)

    df = pd.DataFrame(records).set_index("date")
    df.index = pd.to_datetime(df.index)
    return clean_and_fill(df)


def clean_and_fill(df: pd.DataFrame) -> pd.DataFrame:
    """Interpolate small gaps and back/forward fill edges."""
    df = df.copy()
    df = df.asfreq("D")
    df = df.interpolate(method="time").ffill().bfill()
    return df
