"""
TERRA SHIELD - End-to-End Ingestion & Spatial Verification Script
Verifies hardware node API keys, store-and-forward delayed-alert detection,
PostGIS broadcast audience preview, and nearest contacts.
"""

import sys
import time
import requests
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000"
PHY_KEY = "ts_live_phy-01_64f88c22889172f1b5b5fba7"

def test_single_ingest():
    print("Test 1: Ingest reading with valid X-API-Key on PHY-01...")
    payload = {
        "node_code": "PHY-01",
        "water_level_cm": 245.0,
        "temperature_c": 27.5,
        "humidity": 65.0,
        "pm25": 28.0,
        "battery_pct": 98.0,
        "rssi": -65.0
    }
    resp = requests.post(
        f"{BASE_URL}/api/v1/ingest/reading",
        json=payload,
        headers={"X-API-Key": PHY_KEY, "Content-Type": "application/json"}
    )
    assert resp.status_code in (200, 201), f"Expected 200/201, got {resp.status_code}: {resp.text}"
    data = resp.json()
    print(f"  [PASS] Ingested successfully: reading_id={data.get('reading_id')}, status={data.get('status')}")

def test_unauthorized_ingest():
    print("Test 2: Ingest reading with invalid X-API-Key...")
    payload = {"node_code": "PHY-01", "water_level_cm": 200.0}
    resp = requests.post(
        f"{BASE_URL}/api/v1/ingest/reading",
        json=payload,
        headers={"X-API-Key": "invalid_key_xyz", "Content-Type": "application/json"}
    )
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
    print(f"  [PASS] Rejected unauthorized request correctly: HTTP {resp.status_code}")

def test_store_and_forward_delayed_alert():
    print("Test 3: Store-and-forward batch flush with delayed outage timestamp...")
    old_time = (datetime.now(timezone.utc) - timedelta(seconds=120)).isoformat()
    batch = {
        "node_code": "PHY-01",
        "items": [
            {
                "type": "alert",
                "node_timestamp": old_time,
                "hazard_type": "flood",
                "severity": "critical",
                "confidence": 0.95,
                "decision_ms": 42,
                "reason": "Stored flood surge alert after 120s offline buffering"
            }
        ]
    }
    resp = requests.post(
        f"{BASE_URL}/api/v1/ingest/batch",
        json=batch,
        headers={"X-API-Key": PHY_KEY, "Content-Type": "application/json"}
    )
    assert resp.status_code in (200, 201), f"Expected 200/201, got {resp.status_code}: {resp.text}"
    data = resp.json()
    print(f"  [PASS] Batch flushed: {data}")

    # Check that alert has delivered_after_outage = True
    alerts_resp = requests.get(f"{BASE_URL}/api/v1/alerts")
    alerts = alerts_resp.json()
    delayed = [a for a in alerts if a.get("delivered_after_outage") and (a.get("node_id") == "PHY-01" or a.get("node_code") == "PHY-01" or "PHY-01" in str(a))]
    assert len(delayed) > 0, "Expected at least one delayed alert with delivered_after_outage=True"
    print(f"  [PASS] Verified delayed alert present: delivered_after_outage=True")

def test_broadcast_preview():
    print("Test 4: PostGIS ST_DWithin targeted broadcast preview...")
    resp = requests.get(f"{BASE_URL}/api/v1/alerts/broadcast/preview?lat=30.0869&lng=78.2676&radius_km=15")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    print(f"  [PASS] Calculated audience in 15km radius: {data['recipients_count']} citizens")

def test_knn_contacts():
    print("Test 5: PostGIS KNN nearest contacts query...")
    resp = requests.get(f"{BASE_URL}/api/v1/contacts?near=30.0869,78.2676")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    contacts = resp.json()
    assert len(contacts) > 0
    print(f"  [PASS] Found {len(contacts)} contacts. Nearest: {contacts[0]['name']} ({contacts[0].get('distance_km', 0):.2f} km)")

if __name__ == "__main__":
    print("==================================================")
    print("TERRA SHIELD API & HARDWARE INGESTION TEST")
    print("==================================================")
    try:
        test_single_ingest()
        test_unauthorized_ingest()
        test_store_and_forward_delayed_alert()
        test_broadcast_preview()
        test_knn_contacts()
        print("==================================================")
        print("SUCCESS: ALL INGESTION & SPATIAL TESTS PASSED!")
        print("==================================================")
    except requests.exceptions.ConnectionError:
        print("FAIL: Could not connect to backend at http://127.0.0.1:8000. Is the server running?")
        sys.exit(1)
    except AssertionError as e:
        print(f"FAIL: Test Assertion Error: {e}")
        sys.exit(1)
