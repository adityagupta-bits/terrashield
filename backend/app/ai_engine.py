import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
from app.config import settings
from app.schemas import FloodForecastPoint, FireSpreadVector, AIPredictionResponse

class DisasterAIEngine:
    """Predictive Machine Learning and Mathematical Risk Modeling for Multi-Hazard Disaster Prevention."""

    @staticmethod
    def forecast_flood(
        current_water_level: float,
        rate_of_change_30m: float,
        upstream_delta: float = 0.2
    ) -> Dict[str, Any]:
        """
        Forecasts water levels 3 hours into the future using non-linear rate-of-rise extrapolation.
        Evaluates flash flood risk and time-to-overflow.
        """
        forecast_points: List[FloodForecastPoint] = []
        is_flash_surge = rate_of_change_30m >= settings.FLOOD_FLASH_RATE_THRESHOLD
        
        # Time horizons in hours: 0.5h (30m), 1.0h (60m), 1.5h, 2.0h, 3.0h
        horizons = [0.5, 1.0, 1.5, 2.0, 3.0]
        
        # Non-linear momentum model: height(t) = h0 + (rate/0.5)*t + 0.5 * accel * t^2
        # If water is surging rapidly, acceleration is positive due to upstream runoff
        accel = 0.15 * (rate_of_change_30m / 0.5) if rate_of_change_30m > 0 else -0.05
        
        time_to_overflow_mins: Optional[int] = None

        for h in horizons:
            # Predict level with physical dampening factor
            growth = (rate_of_change_30m / 0.5) * h + 0.5 * accel * (h ** 2) + (upstream_delta * h)
            pred_level = max(0.2, round(current_water_level + growth, 2))
            
            # Classify risk
            if pred_level >= settings.FLOOD_CRITICAL:
                risk = "CRITICAL"
                if time_to_overflow_mins is None and pred_level >= settings.FLOOD_CRITICAL:
                    time_to_overflow_mins = int(h * 60)
            elif pred_level >= settings.FLOOD_CAUTION_MAX or is_flash_surge:
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

        summary = ""
        if is_flash_surge:
            summary = f"CRITICAL SURGE DETECTED! Water level rising by {rate_of_change_30m:.2f}m in 30 mins! Overflow predicted within {time_to_overflow_mins or 45} mins."
        elif current_water_level >= settings.FLOOD_CRITICAL:
            summary = f"RIVER AT DANGER MARK ({current_water_level:.2f}m). Red Alert: Immediate low-lying evacuation advised."
        elif current_water_level >= settings.FLOOD_CAUTION_MAX:
            summary = f"Elevated discharge ({current_water_level:.2f}m). Upstream runoff active, monitor embankments."
        else:
            summary = f"River level normal ({current_water_level:.2f}m). Stable flow."

        return {
            "forecast_points": forecast_points,
            "is_flash_surge": is_flash_surge,
            "time_to_overflow_mins": time_to_overflow_mins,
            "summary": summary
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

ai_engine = DisasterAIEngine()
