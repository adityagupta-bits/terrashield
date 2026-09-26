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

## 📚 4. Comprehensive Engineering Documentation

To distinguish every subsystem, algorithmic proof, and hardware schematic, comprehensive technical documentation is maintained in the `docs/` directory:

| Document | Focus & Content |
|---|---|
| 🥊 [**COMPETITOR_BENCHMARK.md**](file:///c:/Users/ASUS/sih/docs/COMPETITOR_BENCHMARK.md) | **Direct benchmark against TERRA SENTINEL (Team Panchatatva, SIH26178).** Feature matrix, mathematical rigor vs. vague ML, zero-download WhatsApp bot vs. conceptual mobile app, and cost analysis. |
| 📐 [**MATH_AND_MODELS.md**](file:///c:/Users/ASUS/sih/docs/MATH_AND_MODELS.md) | **The Forecasting Mathematics (ARIMA 2,1,1)**: AutoRegressive ($p=2$), Integrated ($d=1$), Moving Average ($q=1$), and **Residual Anomaly Scoring** ($e_t, Z_t \ge 2.5\sigma$). Detailed rationale for why the Citizen Portal strictly omits simulation triggers. |
| ⚡ [**HARDWARE_ARCHITECTURE.md**](file:///c:/Users/ASUS/sih/docs/HARDWARE_ARCHITECTURE.md) | **Edge Sensing Payload**: ESP32-S3-CAM visual edge TinyML, MPU-6050 6-DoF landslide tilt/gyro, capacitive soil moisture v1.2, tipping bucket rain gauge, JSN-SR04T waterproof ultrasonic, pinouts, and 123-day power budget. |
| 📡 [**DECENTRALIZED_MESH_AND_CONSENSUS.md**](file:///c:/Users/ASUS/sih/docs/DECENTRALIZED_MESH_AND_CONSENSUS.md) | **LoRa SX1262 Mesh Protocol**: 32-byte compact binary packet, 61.7ms Time-on-Air, dynamic routing, and Byzantine-Fault-Tolerant ($k$-of-$N$) spatial consensus voting to eliminate false alarms. |
| 🛡️ [**CITIZEN_VS_COMMAND_PORTAL.md**](file:///c:/Users/ASUS/sih/docs/CITIZEN_VS_COMMAND_PORTAL.md) | **Dual-Portal UX Architecture**: Sachet-inspired bilingual Citizen Portal vs. Watermelon UI Gridline EOC Command Center; NDMA guidelines and crisis human factors. |
| 🔌 [**node_payload.md**](file:///c:/Users/ASUS/sih/docs/node_payload.md) | REST API ingestion specification, authentication tokens, batch store-and-forward flushing, and JSON schema definitions. |

---

## 🛠️ 5. Technical Architecture Directory Tree

```
sih/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, /api/v1 routes, WebSocket /ws/live
│   │   ├── ai_engine.py             # Closed-form ARIMA(2,1,1) & Residual Anomaly Z-Score
│   │   ├── auth/                    # JWT tokens & SHA-256 node API key validation
│   │   ├── db/session.py            # PostgreSQL 15 + PostGIS / SQLite spatial engine
│   │   ├── models/                  # SQLAlchemy 2 models (Node, Reading, Alert, etc.)
│   │   ├── routers/                 # Telemetry, Nodes, Alerts, WhatsApp, Simulation
│   │   └── schemas/                 # Pydantic v2 validated schemas with ARIMA fields
│   ├── alembic/                     # Database schema migrations
│   ├── scripts/                     # Seed data & model training
│   ├── docker-compose.yml           # PostGIS 15 production container
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/              # TelemetryPanel, MapView, CitizenView, Navbar
│   │   ├── index.css                # Watermelon UI Gridline design system (Plus Jakarta Sans)
│   │   ├── i18n/                    # English and Hindi dictionary files
│   │   ├── pages/                   # Dashboard, Alerts, Broadcast, CitizenPortal
│   │   └── store/                   # Zustand UI & Auth state stores
│   ├── package.json
│   └── tailwind.config.ts
├── hardware/
│   ├── esp32_firmware/              # ESP32 C++ firmware with LittleFS store-and-forward
│   ├── wokwi/diagram.json           # Virtual ESP32 circuit diagram
│   └── README.md                    # Hardware BOM & wiring guide
├── docs/
│   ├── COMPETITOR_BENCHMARK.md      # Direct comparison vs Terra Sentinel (SIH26178)
│   ├── MATH_AND_MODELS.md           # Mathematical ARIMA & Residual Anomaly formulations
│   ├── HARDWARE_ARCHITECTURE.md     # Multi-hazard sensor payload & power calculations
│   ├── DECENTRALIZED_MESH_AND_CONSENSUS.md # LoRa mesh & BFT consensus algorithm
│   ├── CITIZEN_VS_COMMAND_PORTAL.md # Sachet Citizen vs EOC Command Center analysis
│   └── node_payload.md              # Ingestion API specification
├── simulator/
│   └── iot_mesh_simulator.py        # 20-node mesh simulator with CLI flags
└── start_all.bat                    # One-click launch script
```

---

## 🏆 6. SIH Innovation & Impact Checklist

| Feature Required by SIH26178 | Competitor (TERRA SENTINEL) | TERRA SHIELD Superior Solution |
|---|---|---|
| **Predictive Forecasting** | Vague *"AI/ML techniques"* | **Closed-form ARIMA(2,1,1)** modeling AutoRegressive momentum, stationarity differencing, and Moving Average error decay. |
| **Anomaly Verification** | Naive single threshold | **Standardized Residual Anomaly Scoring** ($e_t = Y_{actual} - \hat{Y}_{arima}$, $Z_t = \frac{\|e_t\|}{\sigma_e} \ge 2.5\sigma$). |
| **False-Alarm Mitigation** | Unspecified neighbor check | **Byzantine-Fault-Tolerant Spatial Consensus**: $k$-of-$N$ topological catchment voting with rate-of-rise correlation. |
| **Resilient Mesh Comms** | Point-to-point LoRa | **Dynamic Multi-Hop LoRa SX1262 Mesh** with autonomous routing and offline store-and-forward LittleFS buffer. |
| **Multiple Hazard Coverage** | Standard sensor array | **Multi-hazard sensing**: Floods (JSN-SR04T), Landslides (MPU-6050 6-DoF + Soil), Wildfires (DHT22 + MQ-135), and Visual (ESP32-S3-CAM). |
| **Community Alert Delivery** | Proposed mobile app (requires download) | **Zero-Download WhatsApp Bot** (500M+ users ready, works on 2G, native location pins, bilingual menus). |
| **Human Ground Truth** | Automated machine alerts only | **Gram Panchayat Sarpanch WhatsApp Loop** verifying field ground truth via NLP before dispatching costly NDRF teams. |
| **Swadeshi Cost Feasibility** | Uncalibrated imports | **Indigenous BOM costing ~₹2,470 ($29 USD)**, 22% cheaper with higher sensor fidelity. |
