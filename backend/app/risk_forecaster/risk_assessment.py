"""
Multi-hazard risk assessment layer for TERRA SHIELD.
Transforms ARIMA point-forecasts into flood, drought, and fire risk assessments
using explainable rule thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any
import pandas as pd

from app.risk_forecaster import config


@dataclass
class RiskAssessment:
    risk_type: str
    triggered: bool
    score: float                  # 0-1 normalized severity indicator
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_type": self.risk_type,
            "triggered": self.triggered,
            "score": round(self.score, 2),
            "reasons": self.reasons
        }


def _safe(df: pd.DataFrame, col: str, default=0.0):
    return df[col] if col in df.columns else pd.Series([default] * len(df))


def assess_flood_risk(forecast_df: pd.DataFrame) -> RiskAssessment:
    t = config.THRESHOLDS["flood"]
    precip = _safe(forecast_df, "precipitation")
    humidity = _safe(forecast_df, "humidity")

    cumulative = float(precip.sum())
    max_single_day = float(precip.max()) if len(precip) else 0.0
    avg_humidity = float(humidity.mean()) if len(humidity) else 0.0

    reasons = []
    triggered = False
    if cumulative >= t["cumulative_precip_mm"]:
        triggered = True
        reasons.append(f"Forecasted cumulative rainfall {cumulative:.1f}mm over horizon exceeds threshold of {t['cumulative_precip_mm']}mm")
    if max_single_day >= t["single_day_precip_mm"]:
        triggered = True
        reasons.append(f"Single-day rainfall projection peaks at {max_single_day:.1f}mm, breaching safety threshold of {t['single_day_precip_mm']}mm")
    if triggered and avg_humidity < t["min_humidity_pct"]:
        reasons.append(f"(Atmospheric note: average humidity {avg_humidity:.0f}% is below the {t['min_humidity_pct']}% saturation guideline)")

    score = min(1.0, cumulative / (t["cumulative_precip_mm"] * 1.5)) if cumulative else 0.0
    return RiskAssessment("flood", triggered, round(score, 2), reasons)


def assess_drought_risk(forecast_df: pd.DataFrame) -> RiskAssessment:
    t = config.THRESHOLDS["drought"]
    precip = _safe(forecast_df, "precipitation")
    humidity = _safe(forecast_df, "humidity")
    temp_max = _safe(forecast_df, "temp_max")

    cumulative = float(precip.sum())
    avg_temp = float(temp_max.mean()) if len(temp_max) else 0.0
    avg_humidity = float(humidity.mean()) if len(humidity) else 0.0

    reasons = []
    triggered = (
        cumulative <= t["max_cumulative_precip_mm"]
        and avg_temp >= t["min_avg_temp_c"]
        and avg_humidity <= t["max_avg_humidity_pct"]
    )
    if triggered:
        reasons.append(f"Near-zero forecasted rainfall ({cumulative:.1f}mm across entire horizon)")
        reasons.append(f"Sustained average max temperature {avg_temp:.1f}°C at or above {t['min_avg_temp_c']}°C")
        reasons.append(f"Average relative humidity {avg_humidity:.0f}% at or below {t['max_avg_humidity_pct']}%")

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

    cumulative = float(precip.sum())
    avg_temp = float(temp_max.mean()) if len(temp_max) else 0.0
    avg_humidity = float(humidity.mean()) if len(humidity) else 0.0
    avg_wind = float(wind.mean()) if len(wind) else 0.0

    reasons = []
    triggered = (
        avg_temp >= t["min_avg_temp_c"]
        and avg_humidity <= t["max_avg_humidity_pct"]
        and avg_wind >= t["min_avg_wind_speed_ms"]
        and cumulative <= t["max_cumulative_precip_mm"]
    )
    if triggered:
        reasons.append(f"Elevated temperatures ({avg_temp:.1f}°C avg max), arid air (avg humidity {avg_humidity:.0f}%), "
                        f"and strong winds (avg {avg_wind:.1f} m/s) with near-zero precipitation ({cumulative:.1f}mm)")

    heat = max(0.0, (avg_temp - t["min_avg_temp_c"]) / 8)
    dryness = max(0.0, (t["max_avg_humidity_pct"] - avg_humidity) / t["max_avg_humidity_pct"]) if t["max_avg_humidity_pct"] > 0 else 0.0
    windiness = min(1.0, avg_wind / (t["min_avg_wind_speed_ms"] * 2)) if t["min_avg_wind_speed_ms"] > 0 else 0.0
    score = min(1.0, (heat + dryness + windiness) / 3) if triggered else 0.0
    return RiskAssessment("fire", triggered, round(score, 2), reasons)


def assess_all(forecast_df: pd.DataFrame) -> Dict[str, RiskAssessment]:
    return {
        "flood": assess_flood_risk(forecast_df),
        "drought": assess_drought_risk(forecast_df),
        "fire": assess_fire_risk(forecast_df),
    }
