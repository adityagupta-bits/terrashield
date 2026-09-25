import pytest
from app.ai_engine import ai_engine
from app.whatsapp_bot import whatsapp_bot
from app.database import haversine_distance_km

def test_flood_forecast_normal():
    res = ai_engine.forecast_flood(current_water_level=1.5, rate_of_change_30m=0.05)
    assert not res["is_flash_surge"]
    assert len(res["forecast_points"]) == 5
    assert res["forecast_points"][0].predicted_water_level_m > 0

def test_flood_forecast_flash_surge():
    res = ai_engine.forecast_flood(current_water_level=2.8, rate_of_change_30m=1.65)
    assert res["is_flash_surge"] is True
    assert res["forecast_points"][-1].risk_level == "CRITICAL"

def test_wildfire_spread_calculation():
    vector = ai_engine.calculate_wildfire_spread(
        lat=30.08, lon=78.26, temp_c=43.0, humidity_pct=12.0, wind_speed_kmh=28.0, wind_direction_deg=180.0
    )
    assert vector.fire_danger_index > 30.0
    assert len(vector.cone_polygon_coords) >= 7
    assert vector.propagation_speed_kmh > 0.5

def test_whatsapp_nlp_verification_hindi():
    status_conf, score = whatsapp_bot.analyze_response_nlp("हाँ नदी का पानी बहुत तेजी से भर रहा है, खतरा है")
    assert status_conf == "CONFIRMED"
    assert score >= 0.80

    status_denial, score_denial = whatsapp_bot.analyze_response_nlp("नहीं सब ठीक है, कोई खतरा नहीं है, गलत अलार्म")
    assert status_denial == "FALSE_ALARM"

def test_haversine_distance():
    # Distance between approx 1 deg latitude should be ~111 km
    dist = haversine_distance_km(30.0, 78.0, 31.0, 78.0)
    assert 110.0 <= dist <= 112.0
