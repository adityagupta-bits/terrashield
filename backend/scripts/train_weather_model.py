import os
import sys
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

# Ensure app package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.weather import WeatherForecast

def train_and_populate_weather_forecast():
    """
    Trains GradientBoostingRegressor on historical seasonal weather patterns (monsoon diurnal temperature,
    relative humidity, and atmospheric precipitation) and populates 72-hour forecast into weather_forecasts.
    """
    print("=================================================================")
    print("  TERRA SHIELD - 72-Hour Weather Model Training & Forecast")
    print("=================================================================")

    # 1. Synthesize 14-day continuous hourly weather training set (Rishikesh-Garhwal basin)
    np.random.seed(42)
    n_hours = 336  # 14 days
    hours = np.arange(n_hours)

    # Diurnal temperature cycle: peaks at 14:00 (2:00 PM), dips at 04:00 AM
    diurnal_temp = 27.0 + 6.5 * np.sin(2 * np.pi * (hours - 8) / 24.0) + np.random.normal(0, 0.8, n_hours)

    # Monsoon precipitation pulses
    rain_pulses = np.maximum(0.0, 15.0 * np.sin(2 * np.pi * hours / 72.0) - 4.0 + np.random.normal(0, 2.0, n_hours))

    # Features: hour_of_day, day_of_week, rolling_temp_lag, rolling_rain_lag
    X = []
    y_temp = []
    y_rain = []

    for i in range(24, n_hours):
        hour_of_day = i % 24
        day_of_week = (i // 24) % 7
        lag_temp = diurnal_temp[i - 1]
        lag_rain = rain_pulses[i - 1]

        X.append([hour_of_day, day_of_week, lag_temp, lag_rain])
        y_temp.append(diurnal_temp[i])
        y_rain.append(rain_pulses[i])

    X = np.array(X)
    y_temp = np.array(y_temp)
    y_rain = np.array(y_rain)

    # 2. Train GradientBoosting models
    model_temp = GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42)
    model_temp.fit(X, y_temp)

    model_rain = GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42)
    model_rain.fit(X, y_rain)

    print("GradientBoosting weather models trained successfully.")

    # 3. Generate 72-hour forecast
    db = SessionLocal()
    try:
        # Clear existing forecasts
        db.query(WeatherForecast).delete()

        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        curr_temp = diurnal_temp[-1]
        curr_rain = rain_pulses[-1]

        for step in range(1, 73):
            f_time = now + timedelta(hours=step)
            features = np.array([[f_time.hour, f_time.weekday(), curr_temp, curr_rain]])

            pred_t = float(model_temp.predict(features)[0])
            pred_r = max(0.0, float(model_rain.predict(features)[0]))

            curr_temp = pred_t
            curr_rain = pred_r

            # Categorize Risk Level
            if pred_r > 15.0:
                risk = "high"
            elif pred_r > 5.0 or pred_t > 40.0:
                risk = "medium"
            else:
                risk = "low"

            record = WeatherForecast(
                region="Rishikesh-Garhwal Catchment",
                forecast_time=f_time,
                temp_c=round(pred_t, 1),
                rainfall_mm=round(pred_r, 1),
                risk_level=risk,
                predicted_at=now,
                model_version="gb-v1.0"
            )
            db.add(record)

        db.commit()
        print(f"Generated and populated 72 hours of forecasts into weather_forecasts table.")
        print("=================================================================\n")
    except Exception as e:
        db.rollback()
        print(f"Error saving forecasts: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    train_and_populate_weather_forecast()
