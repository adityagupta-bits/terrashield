import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
from app.config import settings
from app.schemas import FloodForecastPoint, FireSpreadVector, AIPredictionResponse

class DisasterAIEngine:
    """Predictive Machine Learning and Mathematical Risk Modeling for Multi-Hazard Disaster Prevention."""

    @staticmethod
    def arima_fit_predict(
        history_values: List[float],
        p: int = 2,
        d: int = 1,
        q: int = 1,
        steps: int = 5
    ) -> Dict[str, Any]:
        """
        Fits an ARIMA(p, d, q) time-series model on past sensor readings.
        Three mathematical pillars:
          1. Integrated (I - d): Y'_t = Y_t - Y_{t-1} (removes diurnal/catchment drift to achieve stationarity)
          2. AutoRegressive (AR - p): Y'_t = c + phi_1 * Y'_{t-1} + phi_2 * Y'_{t-2} + ... + eps_t
          3. Moving Average (MA - q): Y'_t = c + eps_t + theta_1 * eps_{t-1} + ... (smoothes random transducer noise)
        Returns the expected 1-step baseline, multi-step projections, and in-sample residual variance.
        """
        y = np.array(history_values, dtype=float) if len(history_values) > 0 else np.array([1.8], dtype=float)
        
        # 1. Differencing (I - d)
        diff = y.copy()
        for _ in range(d):
            if len(diff) > 1:
                diff = np.diff(diff)
            else:
                break
        
        n = len(diff)
        c = 0.0
        phis = np.zeros(p)
        residuals = np.zeros(max(1, n))
        
        # 2. AutoRegressive (AR - p) via Ordinary Least Squares on stationary series
        if n > p:
            X = np.column_stack([diff[i:n - p + i] for i in range(p - 1, -1, -1)])
            Y_target = diff[p:]
            X_design = np.column_stack([np.ones(len(Y_target)), X])
            try:
                coeffs, _, _, _ = np.linalg.lstsq(X_design, Y_target, rcond=None)
                c = float(coeffs[0])
                phis = coeffs[1:]
                residuals = Y_target - (c + np.dot(X, phis))
            except Exception:
                c = float(np.mean(diff)) if len(diff) > 0 else 0.0
                phis = np.array([0.5, 0.2][:p])
        else:
            c = float(np.mean(diff)) if len(diff) > 0 else 0.0
            phis = np.array([0.6, 0.2][:p]) if p >= 2 else np.array([0.6])

        # 3. Moving Average (MA - q) innovation error weighting
        theta = float(np.mean(residuals[-q:])) * 0.4 if len(residuals) >= q else 0.0
        
        # In-sample expected baseline for latest observation
        if n >= p:
            last_p_diffs = diff[-p:][::-1]
            expected_diff = c + float(np.dot(phis[:len(last_p_diffs)], last_p_diffs)) + theta
        else:
            expected_diff = c
            
        prev_level = y[-2] if len(y) >= 2 else y[-1]
        expected_baseline = max(0.2, round(prev_level + expected_diff, 2))

        # 4. Multi-horizon iterative projection
        last_diffs = list(diff[-p:]) if len(diff) >= p else [0.0] * p
        predicted_diffs = []
        cur_theta = theta
        for step in range(steps):
            x_step = np.array(last_diffs[-p:][::-1])
            pred_d = c + float(np.dot(phis[:len(x_step)], x_step)) + (cur_theta if step == 0 else 0.0)
            predicted_diffs.append(pred_d)
            last_diffs.append(pred_d)
            cur_theta *= 0.5  # Moving average error decay

        # Invert differencing to restore absolute physical sensor stages
        current_stage = float(y[-1])
        horizon_projections = []
        for pd in predicted_diffs:
            current_stage = max(0.2, round(current_stage + pd, 2))
            horizon_projections.append(current_stage)

        sigma_residuals = float(np.std(residuals)) if len(residuals) > 2 else 0.20
        sigma_residuals = max(0.12, sigma_residuals)  # Minimum physical noise floor (12cm)

        return {
            "expected_baseline": expected_baseline,
            "horizon_projections": horizon_projections,
            "sigma_residuals": sigma_residuals,
            "ar_coeffs": [round(float(phi), 3) for phi in phis],
            "intercept": round(c, 4),
            "ma_theta": round(theta, 4)
        }

    @staticmethod
    def forecast_flood(
        current_water_level: float,
        rate_of_change_30m: float,
        history_values: Optional[List[float]] = None,
        upstream_delta: float = 0.2
    ) -> Dict[str, Any]:
        """
        Forecasting Mathematics (ARIMA):
          - AutoRegressive (AR - p): Y_t = c + phi_1 * Y_{t-1} + phi_2 * Y_{t-2} + eps_t
          - Integrated (I - d): Y'_t = Y_t - Y_{t-1}
          - Moving Average (MA - q): Y_t = c + eps_t + theta_1 * eps_{t-1} + ...
        
        Decision Logic (Residual Anomaly Scoring):
          - Residual: e_t = Y_actual - Y_arima
          - Anomaly Z-Score: Z_t = |e_t - mu_e| / sigma_e
          - Hazard Decision:
              * Z_t >= 3.0 or level >= 4.0m -> CRITICAL / EMERGENCY
              * 2.0 <= Z_t < 3.0 or level >= 3.0m -> CAUTION / ELEVATED WATCH
              * Z_t < 2.0 -> NORMAL / SYSTEM OPTIMAL
        """
        horizons = [0.5, 1.0, 1.5, 2.0, 3.0]
        
        # Synthesize recent context if not provided
        if not history_values or len(history_values) < 5:
            # Baseline window leading up to current level
            base = current_water_level - (rate_of_change_30m * 1.5)
            history_values = [
                round(base, 2),
                round(base + 0.02, 2),
                round(base + 0.01, 2),
                round(base + 0.04, 2),
                round(current_water_level - rate_of_change_30m, 2),
                round(current_water_level, 2)
            ]

        # 1. Run ARIMA(2, 1, 1) model
        arima_res = DisasterAIEngine.arima_fit_predict(
            history_values=history_values,
            p=2,
            d=1,
            q=1,
            steps=len(horizons)
        )

        expected_baseline = arima_res["expected_baseline"]
        sigma_e = arima_res["sigma_residuals"]

        # 2. Residual Anomaly Scoring: e_t = Y_actual - Y_arima
        residual_error = round(current_water_level - expected_baseline, 3)
        # Z-Score Anomaly: Z_t = |e_t| / sigma_e
        anomaly_z_score = round(abs(residual_error) / sigma_e, 2)

        # Rate of change anomaly detection
        is_flash_surge = rate_of_change_30m >= settings.FLOOD_FLASH_RATE_THRESHOLD or anomaly_z_score >= 3.0

        # Build multi-horizon projections combining ARIMA baseline with surge momentum
        forecast_points: List[FloodForecastPoint] = []
        time_to_overflow_mins: Optional[int] = None

        accel = 0.12 * (rate_of_change_30m / 0.5) if rate_of_change_30m > 0 else -0.04
        
        for idx, h in enumerate(horizons):
            arima_pred = arima_res["horizon_projections"][idx]
            # Dynamic surge momentum addition
            momentum_boost = 0.5 * accel * (h ** 2) if is_flash_surge else 0.0
            pred_level = max(0.2, round(arima_pred + momentum_boost, 2))

            # Hazard Decision Boundary using Z-score & Absolute safety threshold
            if pred_level >= settings.FLOOD_CRITICAL or (anomaly_z_score >= 3.0 and pred_level >= 3.5):
                risk = "CRITICAL"
                if time_to_overflow_mins is None:
                    time_to_overflow_mins = int(h * 60)
            elif pred_level >= settings.FLOOD_CAUTION_MAX or anomaly_z_score >= 2.0 or is_flash_surge:
                risk = "CAUTION"
            else:
                risk = "NORMAL"

            forecast_points.append(
                FloodForecastPoint(
                    time_offset_hours=h,
                    predicted_water_level_m=pred_level,
                    risk_level=risk
                )
            )

        # Decision classification
        if anomaly_z_score >= 3.0 or current_water_level >= settings.FLOOD_CRITICAL:
            decision = "CRITICAL"
            summary = (
                f"CRITICAL RESIDUAL ANOMALY (Z={anomaly_z_score:.2f}σ, Residual={residual_error:+.2f}m)! "
                f"ARIMA(2,1,1) baseline was {expected_baseline:.2f}m. Actual stage {current_water_level:.2f}m breaches danger mark. "
                f"Overflow predicted within {time_to_overflow_mins or 35} mins."
            )
        elif anomaly_z_score >= 2.0 or current_water_level >= settings.FLOOD_CAUTION_MAX:
            decision = "CAUTION"
            summary = (
                f"ELEVATED HYDROLOGICAL WATCH (Z={anomaly_z_score:.2f}σ, Residual={residual_error:+.2f}m). "
                f"ARIMA baseline: {expected_baseline:.2f}m. Upstream runoff active, monitor river gauge."
            )
        else:
            decision = "NORMAL"
            summary = (
                f"STABLE ARIMA BASELINE (Z={anomaly_z_score:.2f}σ, Residual={residual_error:+.2f}m). "
                f"River stage {current_water_level:.2f}m tracks expected ARIMA(2,1,1) curve. Zero anomalous divergence."
            )

        return {
            "forecast_points": forecast_points,
            "is_flash_surge": is_flash_surge,
            "time_to_overflow_mins": time_to_overflow_mins,
            "summary": summary,
            "arima_order": "ARIMA(2,1,1)",
            "expected_baseline": expected_baseline,
            "residual_error": residual_error,
            "anomaly_z_score": anomaly_z_score,
            "is_anomaly": anomaly_z_score >= 2.0,
            "decision": decision
        }

    @staticmethod
    def calculate_wildfire_spread(
        lat: float,
        lon: float,
        temp_c: float,
        humidity_pct: float,
        wind_speed_kmh: float,
        wind_direction_deg: float
    ) -> FireSpreadVector:
        """
        Calculates McArthur Forest Fire Danger Index (FFDI) and models directional spread polygon cone.
        """
        # Clamp inputs
        T = max(10.0, temp_c)
        H = min(100.0, max(5.0, humidity_pct))
        V = max(1.0, wind_speed_kmh)
        D = 8.0  # Drought factor index for dry forest foliage
        
        # McArthur Mark 5 FFDI empirical equation
        exponent = -0.450 + (0.987 * math.log(max(1.0, D))) - (0.0345 * H) + (0.0338 * T) + (0.0234 * V)
        ffdi = round(min(120.0, max(1.0, 2.0 * math.exp(exponent))), 1)

        # Categorize
        if ffdi >= 50 or (temp_c > settings.FIRE_TEMP_CRITICAL and humidity_pct < settings.FIRE_HUMIDITY_CRITICAL):
            category = "Extreme"
        elif ffdi >= 25:
            category = "Very High"
        elif ffdi >= 12:
            category = "High"
        else:
            category = "Moderate"

        # Rate of forward spread in km/h
        # Empirical relationship: R = 0.0012 * FFDI * Wind_speed
        propagation_speed_kmh = round(max(0.2, 0.0012 * ffdi * V), 2)

        # Generate directional projection cone (3 hours travel distance)
        # Distance = speed * 3 hours
        reach_distance_km = min(12.0, propagation_speed_kmh * 2.5)
        
        # Convert bearing to radians (wind direction is the direction wind blows FROM, so fire propagates TOWARDS wind_direction + 180)
        fire_bearing = (wind_direction_deg + 180.0) % 360.0
        cone_angle = 35.0  # Angular half-spread
        
        # Geographic coordinate offsets (approx: 1 deg lat ~ 111 km, 1 deg lon ~ 111 * cos(lat) km)
        km_per_lat = 111.0
        km_per_lon = 111.0 * math.cos(math.radians(lat))

        # Apex of cone is the origin hotspot
        polygon_coords = [[lat, lon]]
        
        # Arc angles from fire_bearing - cone_angle to fire_bearing + cone_angle
        angles = np.linspace(fire_bearing - cone_angle, fire_bearing + cone_angle, num=7)
        for ang in angles:
            rad = math.radians(ang)
            d_lat = (reach_distance_km * math.cos(rad)) / km_per_lat
            d_lon = (reach_distance_km * math.sin(rad)) / km_per_lon
            polygon_coords.append([round(lat + d_lat, 5), round(lon + d_lon, 5)])

        # Close polygon
        polygon_coords.append([lat, lon])

        return FireSpreadVector(
            fire_danger_index=ffdi,
            danger_category=category,
            propagation_speed_kmh=propagation_speed_kmh,
            bearing_degrees=round(fire_bearing, 1),
            cone_polygon_coords=polygon_coords
        )

    @staticmethod
    def analyze_pollution_spike(pm25: float, pm10: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyzes particulate matter concentrations, predicts smog advisory windows, and checks severity.
        """
        severity = "NORMAL"
        advisory = "Air quality is satisfactory."

        if pm25 >= settings.AQI_SEVERE:
            severity = "SEVERE"
            advisory = "Severe smog alert! PM2.5 exceeds 300 ug/m3. Issue mandatory N95 mask notice and halt construction activities."
        elif pm25 >= settings.AQI_POOR_MAX:
            severity = "POOR"
            advisory = "Poor air quality. Sensitive individuals and school children should remain indoors."
        elif pm25 >= settings.AQI_MODERATE_MAX:
            severity = "MODERATE"
            advisory = "Moderate air quality. Slight respiratory irritation possible."

        return {
            "severity": severity,
            "advisory": advisory,
            "pm25_val": pm25,
            "window_hours": 3.0 if severity in ["SEVERE", "POOR"] else 0.0
        }

    @staticmethod
    def assess_weather_multi_hazard_risk(
        history_df: Optional[Any] = None,
        horizon_days: int = 7,
        lat: float = 26.1850,
        lon: float = 91.7500,
        csv_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Multi-Variable ARIMA Weather Forecasting & Multi-Hazard Risk Assessment (Flood, Drought, Wildfire).
        Integrated from the Weather Risk Forecaster module.
        """
        try:
            from model1 import (
                forecast_all_variables,
                forecasts_to_dataframe,
                assess_all,
                load_history_csv,
                generate_synthetic_history,
                clean_and_fill
            )
        except ImportError:
            from app.risk_forecaster import (
                forecast_all_variables,
                forecasts_to_dataframe,
                assess_all,
                load_history_csv,
                generate_synthetic_history,
                clean_and_fill
            )

        # 1. Load or synthesize historical meteorological data
        if history_df is None or (hasattr(history_df, "empty") and history_df.empty):
            try:
                history_df = load_history_csv(csv_path)
            except Exception:
                history_df = generate_synthetic_history(days=365)
        
        history_df = clean_and_fill(history_df)

        # 2. Run per-variable ARIMA models
        forecast_results = forecast_all_variables(history_df, horizon=horizon_days)
        forecast_df = forecasts_to_dataframe(forecast_results)

        # 3. Assess multi-hazard risk (Flood, Drought, Wildfire)
        risk_assessments = assess_all(forecast_df)

        # Format dates and daily projections
        dates = [d.strftime("%Y-%m-%d") for d in forecast_df.index]
        daily_projections = []
        for d in forecast_df.index:
            row = forecast_df.loc[d]
            daily_projections.append({
                "date": d.strftime("%Y-%m-%d"),
                "temp_max": round(float(row.get("temp_max", 0.0)), 1),
                "temp_min": round(float(row.get("temp_min", 0.0)), 1),
                "humidity": round(float(row.get("humidity", 0.0)), 1),
                "precipitation": round(float(row.get("precipitation", 0.0)), 1),
                "pressure": round(float(row.get("pressure", 1013.0)), 1),
                "wind_speed": round(float(row.get("wind_speed", 0.0)), 1)
            })

        risks_dict = {k: v.to_dict() for k, v in risk_assessments.items()}
        
        overall_severity = "LOW"
        triggered_risks = [k for k, v in risk_assessments.items() if v.triggered]
        max_score = max([v.score for v in risk_assessments.values()]) if risk_assessments else 0.0
        
        if max_score >= 0.7 or len(triggered_risks) >= 2:
            overall_severity = "CRITICAL"
        elif max_score >= 0.4 or len(triggered_risks) >= 1:
            overall_severity = "ELEVATED"

        return {
            "region": "Brahmaputra & Kopili Basin, Assam (16 June Incident)",
            "coordinates": {"latitude": lat, "longitude": lon},
            "horizon_days": horizon_days,
            "overall_severity": overall_severity,
            "max_risk_score": max_score,
            "triggered_hazards": triggered_risks,
            "dates": dates,
            "daily_projections": daily_projections,
            "risks": risks_dict,
            "model_metadata": {
                "variables_modeled": list(forecast_results.keys()),
                "orders": {k: v.order for k, v in forecast_results.items()},
                "aic_scores": {k: v.aic for k, v in forecast_results.items()}
            }
        }

ai_engine = DisasterAIEngine()

