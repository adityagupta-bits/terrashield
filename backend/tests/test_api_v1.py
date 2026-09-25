import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.nodes import Node
from app.auth.security import hash_api_key

client = TestClient(app)

@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    yield session
    session.close()

def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "OPERATIONAL"
    assert data["version"] == "2.0.0"

def test_auth_login_valid():
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@terrashield.gov.in",
        "password": "admin123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["role"] == "authority"

def test_auth_login_invalid():
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@terrashield.gov.in",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401

def test_nodes_list():
    resp = client.get("/api/v1/nodes")
    assert resp.status_code == 200
    nodes = resp.json()
    assert len(nodes) >= 20
    # Check physical nodes present
    phy_codes = [n["code"] for n in nodes if not n["is_simulated"]]
    assert "PHY-01" in phy_codes

def test_node_detail_and_readings():
    resp = client.get("/api/v1/nodes/PHY-01")
    assert resp.status_code == 200
    node = resp.json()
    assert node["code"] == "PHY-01"

    # Readings history
    r_resp = client.get("/api/v1/nodes/PHY-01/readings?limit=10")
    assert r_resp.status_code == 200
    assert isinstance(r_resp.json(), list)

def test_ingest_reading_with_valid_key(db_session):
    # Using master simulator key
    headers = {"X-API-Key": "ts_sim_master_key_2026"}
    payload = {
        "node_code": "NODE-01",
        "water_level_cm": 172.5,
        "water_rate_cm_min": 0.4,
        "temperature_c": 25.4,
        "humidity": 60.0,
        "battery_pct": 94.0,
        "rssi": -65.0
    }
    resp = client.post("/api/v1/ingest/reading", json=payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["node_code"] == "NODE-01"

def test_ingest_reading_invalid_key():
    headers = {"X-API-Key": "invalid_bogus_key"}
    payload = {
        "node_code": "NODE-01",
        "water_level_cm": 150.0
    }
    resp = client.post("/api/v1/ingest/reading", json=payload, headers=headers)
    assert resp.status_code == 401

def test_ingest_alert_normal_and_delayed():
    headers = {"X-API-Key": "ts_sim_master_key_2026"}

    # 1. Normal alert (current timestamp, delay <= 60s)
    now = datetime.utcnow()
    normal_payload = {
        "node_code": "NODE-02",
        "node_timestamp": now.isoformat(),
        "hazard_type": "flood",
        "severity": "critical",
        "confidence": 0.94,
        "decision_ms": 38,
        "reason": "Water rise > 8 cm/min"
    }
    resp1 = client.post("/api/v1/ingest/alert", json=normal_payload, headers=headers)
    assert resp1.status_code == 200
    assert resp1.json()["delivered_after_outage"] is False

    # 2. Delayed alert (> 60s old, simulating delivery after outage)
    past_ts = now - timedelta(minutes=5)
    delayed_payload = {
        "node_code": "NODE-03",
        "node_timestamp": past_ts.isoformat(),
        "hazard_type": "flood",
        "severity": "critical",
        "confidence": 0.91,
        "decision_ms": 40,
        "reason": "Store-and-forward alert flushed after connection recovery"
    }
    resp2 = client.post("/api/v1/ingest/alert", json=delayed_payload, headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["delivered_after_outage"] is True

def test_batch_store_and_forward():
    headers = {"X-API-Key": "ts_sim_master_key_2026"}
    past_time = datetime.utcnow() - timedelta(minutes=10)

    batch_payload = {
        "node_code": "NODE-03",
        "items": [
            {
                "type": "reading",
                "ts": (past_time + timedelta(minutes=1)).isoformat(),
                "water_level_cm": 210.0,
                "water_rate_cm_min": 1.2
            },
            {
                "type": "alert",
                "node_timestamp": (past_time + timedelta(minutes=2)).isoformat(),
                "hazard_type": "flood",
                "severity": "critical",
                "confidence": 0.93,
                "decision_ms": 40,
                "reason": "Outage queued surge alert"
            }
        ]
    }
    resp = client.post("/api/v1/ingest/batch", json=batch_payload, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "batch_flushed"
    assert data["processed_alerts"] == 1
    assert data["processed_readings"] == 1

def test_broadcast_preview_and_send():
    # Preview
    resp = client.get("/api/v1/alerts/broadcast/preview?lat=30.0869&lng=78.2676&radius_km=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "recipients_count" in data
    assert data["recipients_count"] > 0

    # Dispatch Broadcast
    send_payload = {
        "lat": 30.0869,
        "lng": 78.2676,
        "radius_km": 5.0,
        "template_id": "flood_warning"
    }
    resp_send = client.post("/api/v1/alerts/broadcast", json=send_payload)
    assert resp_send.status_code == 200
    assert resp_send.json()["recipients_count"] > 0

def test_contacts_knn_sorting():
    resp = client.get("/api/v1/contacts?near=30.0869,78.2676")
    assert resp.status_code == 200
    contacts = resp.json()
    assert len(contacts) > 10
    # First contact should be closest
    assert contacts[0]["distance_km"] <= contacts[-1]["distance_km"]

def test_weather_and_forecast():
    # Current
    c_resp = client.get("/api/v1/weather/current")
    assert c_resp.status_code == 200
    assert "temp_c" in c_resp.json()

    # Forecast
    f_resp = client.get("/api/v1/weather/forecast")
    assert f_resp.status_code == 200
    fdata = f_resp.json()
    assert len(fdata["points"]) > 0
    assert fdata["note"] == "Forecast based on past weather data"

def test_citizen_status():
    resp = client.get("/api/v1/citizen/status?lat=30.0869&lng=78.2676&lang=en")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ["safe", "caution", "evacuate"]
    assert len(data["nearest_shelters"]) > 0

def test_demo_controls():
    # Trigger flood on Node 2
    trig_resp = client.post("/api/v1/demo/trigger", json={
        "node_id": "NODE-02",
        "type": "flood"
    })
    assert trig_resp.status_code == 200

    # Cut network on Node 3
    cut_resp = client.post("/api/v1/demo/network", json={
        "node_id": "NODE-03",
        "action": "cut"
    })
    assert cut_resp.status_code == 200
    assert cut_resp.json()["status"] == "cut"

    # Restore network on Node 3
    restore_resp = client.post("/api/v1/demo/network", json={
        "node_id": "NODE-03",
        "action": "restore"
    })
    assert restore_resp.status_code == 200
    assert restore_resp.json()["status"] == "restored"
    assert restore_resp.json()["flushed_alerts"] >= 1
