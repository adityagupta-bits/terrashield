"""
Turns ARIMA point-forecasts into flood / drought / fire risk assessments
using the threshold rules in config.THRESHOLDS.

This is intentionally a transparent, editable rule layer rather than a black
box: every risk decision below can be traced to a specific number you can
tune for your region. If you later get labeled historical disaster events,
swap this module out for a trained classifier (e.g. logistic regression /
random forest) fed the same forecast features - the rest of the pipeline
doesn't need to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import pandas as pd

import config


@dataclass
class RiskAssessment:
    risk_type: str
    triggered: bool
    score: float                  # 0-1 rough severity indicator
    reasons: List[str] = field(default_factory=list)


def _safe(df: pd.DataFrame, col: str, default=0.0):
    return df[col] if col in df.columns else pd.Series([default] * len(df))


def assess_flood_risk(forecast_df: pd.DataFrame) -> RiskAssessment:
    t = config.THRESHOLDS["flood"]
    precip = _safe(forecast_df, "precipitation")
    humidity = _safe(forecast_df, "humidity")

    cumulative = precip.sum()
    max_single_day = precip.max() if len(precip) else 0
    avg_humidity = humidity.mean()

    reasons = []
    triggered = False
    if cumulative >= t["cumulative_precip_mm"]:
        triggered = True
        reasons.append(f"forecasted cumulative rainfall {cumulative:.1f}mm over horizon exceeds {t['cumulative_precip_mm']}mm")
    if max_single_day >= t["single_day_precip_mm"]:
        triggered = True
        reasons.append(f"a single day forecasts {max_single_day:.1f}mm, exceeding {t['single_day_precip_mm']}mm")
    if triggered and avg_humidity < t["min_humidity_pct"]:
        reasons.append(f"(note: avg humidity {avg_humidity:.0f}% is below the {t['min_humidity_pct']}% saturation guideline)")

    score = min(1.0, cumulative / (t["cumulative_precip_mm"] * 1.5)) if cumulative else 0.0
    return RiskAssessment("flood", triggered, round(score, 2), reasons)


def assess_drought_risk(forecast_df: pd.DataFrame) -> RiskAssessment:
    t = config.THRESHOLDS["drought"]
    precip = _safe(forecast_df, "precipitation")
    humidity = _safe(forecast_df, "humidity")
    temp_max = _safe(forecast_df, "temp_max")

    cumulative = precip.sum()
    avg_temp = temp_max.mean()
    avg_humidity = humidity.mean()

    reasons = []
    triggered = (
        cumulative <= t["max_cumulative_precip_mm"]
        and avg_temp >= t["min_avg_temp_c"]
        and avg_humidity <= t["max_avg_humidity_pct"]
    )
    if triggered:
        reasons.append(f"near-zero forecasted rainfall ({cumulative:.1f}mm over horizon)")
        reasons.append(f"avg max temp {avg_temp:.1f}°C at/above {t['min_avg_temp_c']}°C")
        reasons.append(f"avg humidity {avg_humidity:.0f}% at/below {t['max_avg_humidity_pct']}%")

    dryness = max(0.0, (t["max_cumulative_precip_mm"] - cumulative + 1) / (t["max_cumulative_precip_mm"] + 1))
    heat = max(0.0, (avg_temp - t["min_avg_temp_c"]) / 10)
    score = min(1.0, 0.5 * dryness + 0.5 * heat) if triggered else 0.0
    return RiskAssessment("drought", triggered, round(score, 2), reasons)


def assess_fire_risk(forecast_df: pd.DataFrame) -> RiskAssessment:
    t = config.THRESHOLDS["fire"]
    precip = _safe(forecast_df, "precipitation")
    humidity = _safe(forecast_df, "humidity")
    temp_max = _safe(forecast_df, "temp_max")
    wind = _safe(forecast_df, "wind_speed")

    cumulative = precip.sum()
    avg_temp = temp_max.mean()
    avg_humidity = humidity.mean()
    avg_wind = wind.mean()

    reasons = []
    triggered = (
        avg_temp >= t["min_avg_temp_c"]
        and avg_humidity <= t["max_avg_humidity_pct"]
        and avg_wind >= t["min_avg_wind_speed_ms"]
        and cumulative <= t["max_cumulative_precip_mm"]
    )
    if triggered:
        reasons.append(f"hot ({avg_temp:.1f}°C avg max), dry (avg humidity {avg_humidity:.0f}%), "
                        f"and windy (avg {avg_wind:.1f} m/s) with almost no rain ({cumulative:.1f}mm)")

    heat = max(0.0, (avg_temp - t["min_avg_temp_c"]) / 8)
    dryness = max(0.0, (t["max_avg_humidity_pct"] - avg_humidity) / t["max_avg_humidity_pct"])
    windiness = min(1.0, avg_wind / (t["min_avg_wind_speed_ms"] * 2))
    score = min(1.0, (heat + dryness + windiness) / 3) if triggered else 0.0
    return RiskAssessment("fire", triggered, round(score, 2), reasons)


def assess_all(forecast_df: pd.DataFrame) -> Dict[str, RiskAssessment]:
    return {
        "flood": assess_flood_risk(forecast_df),
        "drought": assess_drought_risk(forecast_df),
        "fire": assess_fire_risk(forecast_df),
    }
