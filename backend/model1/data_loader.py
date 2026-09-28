"""
Data acquisition layer.

Three ways to get data in:
  1. fetch_history_from_api()   -> pulls daily summaries from OpenWeather
                                    (limited lookback depending on your plan)
  2. load_history_csv()         -> load your own longer historical record
                                    (recommended for real ARIMA training)
  3. generate_synthetic_history() -> quick fake data so you can test the
                                    whole pipeline end-to-end without an
                                    API key or a CSV.
"""

from __future__ import annotations

import datetime as dt
import time
from typing import Optional

import numpy as np
import pandas as pd
import requests

import config


def fetch_history_from_api(
    lat: float,
    lon: float,
    api_key: str,
    days: int = config.HISTORY_DAYS_TO_FETCH,
    request_delay_sec: float = 1.0,
) -> pd.DataFrame:
    """
    Pull `days` of daily weather summaries ending yesterday from OpenWeather's
    One Call 3.0 "day_summary" endpoint, one HTTP request per day.

    Requires a paid/subscribed OpenWeather plan for historical access; the
    free tier will return 401/403 for these dates. Rate-limited with a small
    delay between requests to stay under typical per-minute call caps.

    Returns a DataFrame indexed by date with columns matching
    config.TARGET_VARIABLES.
    """
    if not api_key:
        raise ValueError("No OpenWeather API key provided (set OPENWEATHER_API_KEY).")

    records = []
    today = dt.date.today()

    for i in range(days, 0, -1):
        day = today - dt.timedelta(days=i)
        params = {
            "lat": lat,
            "lon": lon,
            "date": day.isoformat(),
            "appid": api_key,
            "units": "metric",
        }
        resp = requests.get(config.ONECALL_DAY_SUMMARY_URL, params=params, timeout=15)
        if resp.status_code != 200:
            print(f"  [warn] {day}: HTTP {resp.status_code} - {resp.text[:150]}")
            time.sleep(request_delay_sec)
            continue

        d = resp.json()
        try:
            records.append({
                "date": day,
                "temp_max": d["temperature"]["max"],
                "temp_min": d["temperature"]["min"],
                "humidity": d["humidity"]["afternoon"],
                "precipitation": d.get("precipitation", {}).get("total", 0.0),
                "pressure": d["pressure"]["afternoon"],
                "wind_speed": d["wind"]["max"]["speed"],
            })
        except KeyError as e:
            print(f"  [warn] {day}: unexpected response shape, missing {e}")

        time.sleep(request_delay_sec)

    if not records:
        raise RuntimeError(
            "No historical records could be fetched. Your OpenWeather plan may not "
            "include historical access, or the location/date range is invalid. "
            "Consider load_history_csv() instead."
        )

    df = pd.DataFrame(records).set_index("date")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def load_history_csv(path: str, date_col: str = "date") -> pd.DataFrame:
    """
    Load historical weather data from a CSV you already have (e.g. exported
    from NASA POWER, NOAA, IMD, a utility's climate portal, etc).

    Expected columns (case-insensitive, extras are ignored):
      date, temp_max, temp_min, humidity, precipitation, pressure, wind_speed

    Missing target columns are filled with NaN and interpolated later.
    """
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
    Generate a plausible-looking synthetic daily weather history so the
    ARIMA + risk-classification pipeline can be exercised without any
    network access or real data. NOT for real predictions.
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=dt.date.today() - dt.timedelta(days=1), periods=days, freq="D")

    day_of_year = dates.dayofyear.values
    seasonal_temp = 27 + 8 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    temp_max = seasonal_temp + rng.normal(2, 1.5, days)
    temp_min = seasonal_temp - 6 + rng.normal(0, 1.2, days)

    # Monsoon-like precipitation bump mid-year, mostly dry otherwise
    monsoon = np.clip(np.sin(2 * np.pi * (day_of_year - 150) / 365), 0, None) ** 2
    precipitation = np.clip(rng.exponential(2 + 25 * monsoon, days) - 2, 0, None)

    humidity = np.clip(45 + 35 * monsoon + rng.normal(0, 5, days), 10, 100)
    pressure = 1013 + rng.normal(0, 4, days) - 3 * monsoon
    wind_speed = np.clip(3 + rng.normal(0, 1.5, days) + 2 * monsoon, 0, None)

    df = pd.DataFrame(
        {
            "temp_max": temp_max,
            "temp_min": temp_min,
            "humidity": humidity,
            "precipitation": precipitation,
            "pressure": pressure,
            "wind_speed": wind_speed,
        },
        index=dates,
    )
    return df


def clean_and_fill(df: pd.DataFrame) -> pd.DataFrame:
    """Interpolate small gaps, forward/back-fill edges, so ARIMA gets a clean series."""
    df = df.copy()
    df = df.asfreq("D")  # ensures a continuous daily index, introduces NaN for gaps
    df = df.interpolate(method="time").ffill().bfill()
    return df
