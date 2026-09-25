# TERRA SHIELD 🛡️
### Resilient, AI-Powered Environmental Monitoring Network for Early Hazard Detection & Actionable Alerts
**Problem Statement ID:** SIH26178 | **Theme:** Disaster Management  
**Category:** Hardware / Software Hybrid | **Team Name:** TERRA SHIELD  

---

## 📌 1. Executive Summary & Problem Alignment

In catastrophic disasters such as sudden flash floods, cyclonic surges, and wildfires across India (e.g. Wayanad landslides, Uttarakhand cloudbursts, Assam floods), **cellular towers and internet grids are usually the very first critical infrastructure to collapse**. Furthermore, existing early warning mechanisms are purely reactive (triggering alerts only after water levels overflow) and suffer from false alarms that waste massive National Disaster Response Force (NDRF) and civil protection resources.

**TERRA SHIELD** introduces an end-to-end multi-hazard architecture designed specifically for the Indian subcontinent:
1. **Decentralized Edge Mesh Network (Zero-Internet Resilient Communication)**:
   - Ultra-low-cost indigenous sensor nodes powered by the **ESP32** microcontroller.
   - Operates over an ad-hoc, peer-to-peer **ESP-NOW & LoRa SX1278 multi-hop mesh network**. Even if cellular towers collapse, packets hop node-to-node across canyons and flood plains until reaching an active emergency sink.
   - **LittleFS On-Device Ring Buffer**: Stores up to 200 telemetry records when disconnected from field cellular gateways. Flushes batch to backend when comms return, with automatic `DELIVERED AFTER OUTAGE` delay detection.
2. **Predictive Forecasting & On-Device Decision Timing**:
   - **Microsecond On-Device Edge Timing**: Evaluates rate-of-change ($\Delta h / \Delta t$) and triggers local sirens in < 5ms before cloud receipt.
   - **72-Hour Precipitation & Inflow Forecast**: Trained Scikit-learn GradientBoosting model forecasting river water rise and precipitation trends across Upper Ganges catchments.
3. **Vernacular Voice & WhatsApp Bot Crowdsourcing ("Human-as-a-Sensor")**:
   - Automated two-way WhatsApp query dispatched in regional Indian languages (Hindi, English) to Gram Panchayat Sarpanches and ward councillors.
   - Multilingual NLP parses citizen replies, verifying ground reality before triggering high-cost emergency NDRF deployments.
   - Citizen WhatsApp bot with 1-5 numbered menus for immediate advisory, safe shelter directions, and reporting.
4. **Dual Presentation Portals**:
   - **Authorities Command & Control Center** (`/`): Tactical dark-mode GIS heatmaps, 20 nodes with hardware `PHY` badges, live alert registry with delayed-outage tags, PostGIS targeted broadcast builder, nearest emergency contacts (KNN), weather forecasts, and mesh topology visualizer.
   - **Citizen Mobile Advisory Portal** (`/citizen`): Lightweight, accessible light-theme interface with English/Hindi toggle, GPS geofenced safety status ("SAFE", "ADVISORY", "EVACUATE"), and Google Maps directions to nearest high-ground shelters.

---

## 🚀 2. Quick Start Guide (One-Click Launch)

### Prerequisites
- Python 3.10+
- Node.js v18+ & npm
- (Optional) Docker for PostgreSQL 15 + PostGIS (transparent SQLite fallback active by default for local development)

### Launching Everything Simultaneously
Double-click:
```bat
start_all.bat
```
This automatically starts:
1. **Backend & AI Engine** on [http://localhost:8000](http://localhost:8000) (Swagger Docs at `/docs`)
2. **Authorities Command Center** on [http://localhost:5173](http://localhost:5173)
3. **20-Node Autonomous IoT Mesh Simulator** (5 physical + 15 simulated) streaming realistic telemetry packets

### Running Verification Tests
```bash
# Backend pytest suite (14/14 tests passing)
backend\venv\Scripts\python.exe -m pytest backend/tests/test_api_v1.py -v

# Hardware ingestion & spatial PostGIS verification script
backend\venv\Scripts\python.exe scripts/test_ingest.py

# Frontend production build verification
cd frontend && npm run build
```

---

## 🕹️ 3. Step-by-Step Live Demonstration Script for Hackathon Judges

### Step 1: Show Baseline Multi-Node Mesh Monitoring
1. Open [http://localhost:5173](http://localhost:5173).
2. Point out the **20 active nodes** (5 physical hardware nodes marked with green `PHY` badges + 15 mesh relays) across the Rishikesh-Garhwal catchment basin.
3. Show the **GIS Incident & Threat Map** with live color-coded node markers, GeoJSON hazard polygons, and designated safe shelters.
4. Click on any node or **"Mesh Topology"** in the sidebar:
   - Point out battery levels, RSSI, and multi-hop relay edges.

### Step 2: Demonstrate Resilient Offline Cellular Blackout Mode
1. In the bottom dock, click **"Blackout"**.
2. **Observe**:
   - Primary gateway on `NODE-08` is severed.
   - Packets dynamically reroute through `NODE-02` and `PHY-01` via LoRa P2P.
   - Explain to judges: *"Even if cellular towers are washed away by landslides or floods, our distributed mesh continues transmitting life-saving telemetry."*

### Step 3: Demonstrate Field Outage & Store-and-Forward Delayed Alerts
1. In the bottom dock, click **"Cut Comms"** on target node `PHY-01`.
2. Readings begin buffering to on-device LittleFS flash memory.
3. After 10 seconds, click **"Restore Comms"**.
4. The batch is flushed to `/api/v1/ingest/store-forward`.
5. In the Incident Queue and Alerts page, show the prominent amber tag:  
   **`DELIVERED AFTER OUTAGE (Buffered 72s in LittleFS)`**  
   Proves the backend accurately tracks message latency during catastrophic network failure.

### Step 4: Demonstrate "Human-as-a-Sensor" Vernacular WhatsApp Verification
1. Click **"Sarpanch Verify"** on an active alert or navigate to **WhatsApp** in the sidebar.
2. In the interactive phone modal, show the automated notification sent to Gram Pradhan Rameshwar Sharma.
3. Click option **"1: Flood Confirmed"** or type a custom reply.
4. The backend records the ground truth, updates the status to **"VERIFIED"**, and logs an auditable confirmation before dispatching NDRF.
5. Click **"Deploy NDRF"** to log the official rescue battalion deployment!

### Step 5: Demonstrate Targeted PostGIS Broadcast & Citizen Portal
1. Navigate to **Broadcast**:
   - Adjust the radius slider (e.g. 15 km around Shivpuri).
   - Show the dynamic citizen count calculated via PostGIS `ST_DWithin` (187 citizens).
   - Select the bilingual Flash Flood evacuation template and show the English and Hindi previews.
2. Navigate to [http://localhost:5173/citizen](http://localhost:5173/citizen):
   - Switch language to **हिंदी**.
   - Show the live safety status banner, nearest safe shelter with distance (km) and capacity, and Google Maps direction link.

---

## 🛠️ 4. Technical Architecture Details

```
sih/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, /api/v1 routes, WebSocket /ws/live
│   │   ├── auth/                    # JWT tokens & SHA-256 node API key validation
│   │   ├── db/session.py            # PostgreSQL 15 + PostGIS / SQLite spatial engine
│   │   ├── models/                  # SQLAlchemy 2 models (Node, Reading, Alert, etc.)
│   │   ├── routers/v1/              # Ingest, Nodes, Alerts, Broadcast, Contacts, Weather
│   │   └── schemas/                 # Pydantic v2 validated schemas
│   ├── alembic/                     # Database schema migrations
│   ├── scripts/
│   │   ├── seed.py                  # Seed 20 nodes, 21 contacts, 3 hazard zones
│   │   └── train_weather_model.py   # Scikit-learn GradientBoosting 72h forecast
│   ├── docker-compose.yml           # PostGIS 15 production container
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/client.ts            # Typed API client with JWT interceptor
│   │   ├── components/              # MapView, NodeDetailDrawer, DemoControlDock, etc.
│   │   ├── hooks/                   # useWebSocket with backoff, useData React Query
│   │   ├── i18n/                    # English and Hindi dictionary files
│   │   ├── pages/                   # Dashboard, Alerts, Broadcast, Contacts, Weather, News, CitizenPortal, Login
│   │   └── store/                   # Zustand UI & Auth state stores
│   ├── package.json
│   └── tailwind.config.ts
├── hardware/
│   ├── esp32_firmware/
│   │   ├── esp32_firmware.ino       # ESP32 C++ firmware with LittleFS store-and-forward
│   │   └── config.h.example         # Hardware pinouts and API key configuration
│   ├── wokwi/diagram.json           # Virtual ESP32 circuit diagram
│   └── README.md
├── simulator/
│   └── iot_mesh_simulator.py        # 20-node mesh simulator with CLI flags
├── docs/
│   └── node_payload.md              # Ingestion API specification
└── start_all.bat                    # One-click launch script
```

---

## 🏆 5. SIH Innovation & Impact Checklist

| Feature Required by SIH26178 | TERRA SHIELD Solution |
|---|---|
| **Resilient Infrastructure** | Multi-hop decentralized ESP-NOW / LoRa mesh network; keeps transmitting even when cellular towers fail. |
| **Edge AI & Localized Intelligence** | On-device ESP32 rapid surge detection (< 5ms) + Cloud Scikit-learn 72-hour precipitation forecast. |
| **LittleFS Store-and-Forward** | Automatic on-chip flash buffering during network severance with delayed-outage audit trail. |
| **Multiple Hazards in Unified System**| Simultaneous monitoring of Floods (ultrasonic), Wildfires (ambient heat index + wind), and Air Quality (PM2.5/PM10). |
| **Targeted Early Warning** | PostGIS `ST_DWithin` spatial calculation for cell broadcasts, avoiding panic and spam. |
| **Human-as-a-Sensor** | Vernacular WhatsApp chatbot querying Gram Panchayat Sarpanches to confirm ground reality before costly NDRF dispatch. |
| **Swadeshi Ultra-Low-Cost Hardware** | Indigenous open-source ESP32 nodes costing only ~₹1,850 ($22), over 95% cheaper than imported stations. |
