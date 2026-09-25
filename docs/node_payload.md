# TERRA SHIELD Hardware Ingestion & Node Payload Specification

This document specifies the communication contract between physical/simulated edge nodes and the TERRA SHIELD ingestion backend.

---

## 1. Authentication

Every ingestion request from physical and simulated hardware nodes MUST include the `X-API-Key` HTTP header:

```http
POST /api/v1/ingest/reading HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
X-API-Key: ts_live_phy-01_64f88c22889172f1b5b5fba7
```

### Pre-Seeded Physical Node Keys:
- `PHY-01`: `ts_live_phy-01_64f88c22889172f1b5b5fba7`
- `PHY-02`: `ts_live_phy-02_2c740691a988030224cac7bd`
- `PHY-03`: `ts_live_phy-03_60a6f1622ed3586ee0e8d612`
- `PHY-04`: `ts_live_phy-04_d446affeb8efdefb2482c5cc`
- `PHY-05`: `ts_live_phy-05_8c3727d15f4cf097a7ee1067`
- Simulator Master Key: `ts_sim_master_key_2026`

---

## 2. Live Telemetry Ingestion (`POST /api/v1/ingest/reading`)

### Request Body:
```json
{
  "node_id": "PHY-01",
  "water_level_m": 3.82,
  "water_rate_of_change": 0.45,
  "temperature_c": 28.4,
  "humidity_pct": 78.0,
  "pm25": 42.5,
  "battery_pct": 98.2,
  "mesh_hops": 0,
  "edge_emergency_flag": true,
  "decision_latency_us": 420,
  "timestamp": "2026-09-19T21:15:00Z"
}
```

### Response (`201 Created`):
```json
{
  "status": "ingested",
  "reading_id": 1420,
  "node_id": "PHY-01",
  "alert_triggered": true,
  "delivered_after_outage": false
}
```

---

## 3. Store-and-Forward Batch Flush (`POST /api/v1/ingest/store-forward`)

When an edge node experiences field cellular or gateway severance, readings are recorded to flash storage (`LittleFS` ring buffer `/buffer.jsonl`). When connectivity is restored, the buffer is flushed as a JSON array.

### Request Body:
```json
[
  {
    "node_id": "PHY-01",
    "water_level_m": 4.12,
    "temperature_c": 28.1,
    "humidity_pct": 82.0,
    "pm25": 55.0,
    "battery_pct": 97.5,
    "mesh_hops": 1,
    "edge_emergency_flag": true,
    "timestamp": "2026-09-19T21:05:00Z"
  },
  {
    "node_id": "PHY-01",
    "water_level_m": 4.35,
    "temperature_c": 28.0,
    "humidity_pct": 84.0,
    "pm25": 60.0,
    "battery_pct": 97.1,
    "mesh_hops": 1,
    "edge_emergency_flag": true,
    "timestamp": "2026-09-19T21:10:00Z"
  }
]
```

### Response (`200 OK`):
```json
{
  "status": "batch_flushed",
  "flushed_count": 2,
  "delayed_alerts_created": 1,
  "message": "Store-and-forward batch processed with delayed outage flags."
}
```

### Delayed Alert Detection Logic:
If `timestamp` of a critical reading is older than 60 seconds relative to ingestion receipt time:
- An incident alert is automatically flagged with `delivered_after_outage = true`.
- `delivery_delay_sec` records the elapsed latency (e.g. 72s).
- The Authority Command Center UI displays the prominent amber badge:  
  **`DELIVERED AFTER OUTAGE (Buffered 72s in LittleFS)`**

---

## 4. Edge Anomaly Alert Direct Uplink (`POST /api/v1/ingest/alert`)

```json
{
  "node_id": "PHY-01",
  "hazard_type": "FLASH_FLOOD",
  "severity": "CRITICAL",
  "title": "On-Device Surge Anomaly Detected",
  "description": "Water level delta exceeded 0.40m/min. Local buzzer activated.",
  "sensor_value": 4.35,
  "threshold_value": 4.00,
  "decision_latency_us": 420
}
```
