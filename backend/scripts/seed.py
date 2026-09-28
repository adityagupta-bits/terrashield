import hashlib
import json
import secrets
import os
import sys
from datetime import datetime

# Ensure app package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bcrypt

from app.db.session import SessionLocal
from app.models import (
    Node, Reading, Alert, HazardZone, Contact, Subscriber,
    WhatsAppMessage, BroadcastLog, WeatherObservation,
    WeatherForecast, NewsFlash, User, MeshLink,
    IncidentAlert, WhatsAppVerification, SafeShelter,
    SensorNode, TelemetryRecord
)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def seed_database(force: bool = False):
    db = SessionLocal()
    try:
        print("=================================================================")
        print("  TERRA SHIELD (SIH26178) - Assam 16 June Incident Seeding Engine")
        print("=================================================================")

        if force:
            print("Force flag detected. Clearing existing operational tables...")
            for model in [
                Reading, MeshLink, Alert, WhatsAppVerification, IncidentAlert,
                SafeShelter, Contact, HazardZone, NewsFlash, Subscriber,
                WhatsAppMessage, BroadcastLog, Node, User, SensorNode, TelemetryRecord
            ]:
                try:
                    db.query(model).delete()
                except Exception as ex:
                    print(f"  Note cleaning {model.__name__}: {ex}")
            db.commit()
            print("Existing tables successfully cleared.")
        elif db.query(Node).count() > 0:
            print("Database already contains nodes. Use --force to reseed.")
            return

        # Assam 16 June Incident Focal Point (Brahmaputra - Kopili Basin)
        base_lat = 26.1850
        base_lng = 91.7500

        # -------------------------------------------------------------
        # 1. Physical Sensor Nodes (PHY-01 to PHY-05) - Hardware Sentinels
        # -------------------------------------------------------------
        physical_keys = {}
        physical_nodes_data = [
            {"code": "PHY-01", "name": "Saraighat Brahmaputra River Sentry (Hardware)", "hazard_type": "flood", "lat": 26.1850, "lng": 91.7000, "level": 1, "parent": None},
            {"code": "PHY-02", "name": "Kopili River Bridge Inundation Gauge (Hardware)", "hazard_type": "flood", "lat": 26.0500, "lng": 92.7800, "level": 2, "parent": "PHY-01"},
            {"code": "PHY-03", "name": "Kampur Embankment Critical Sentry (Hardware)", "hazard_type": "flood", "lat": 26.0800, "lng": 92.7400, "level": 3, "parent": "PHY-02"},
            {"code": "PHY-04", "name": "Deepor Beel Catchment Water Watch (Hardware)", "hazard_type": "flood", "lat": 26.1200, "lng": 91.6600, "level": 1, "parent": None},
            {"code": "PHY-05", "name": "Pandu Port Hydrological Telemetry Post (Hardware)", "hazard_type": "flood", "lat": 26.1820, "lng": 91.7150, "level": 1, "parent": None},
        ]

        print("\n--- GENERATING PHYSICAL HARDWARE API KEYS ---")
        created_nodes = {}

        FIXED_PHYSICAL_KEYS = {
            "PHY-01": "ts_live_phy-01_64f88c22889172f1b5b5fba7",
            "PHY-02": "ts_live_phy-02_2c740691a988030224cac7bd",
            "PHY-03": "ts_live_phy-03_60a6f1622ed3586ee0e8d612",
            "PHY-04": "ts_live_phy-04_d446affeb8efdefb2482c5cc",
            "PHY-05": "ts_live_phy-05_8c3727d15f4cf097a7ee1067",
        }

        for pdata in physical_nodes_data:
            plain_key = FIXED_PHYSICAL_KEYS.get(pdata["code"], f"ts_live_{pdata['code'].lower()}_{secrets.token_hex(12)}")
            key_hash = hash_key(plain_key)
            physical_keys[pdata["code"]] = plain_key

            node = Node(
                code=pdata["code"],
                name=pdata["name"],
                hazard_type=pdata["hazard_type"],
                latitude=pdata["lat"],
                longitude=pdata["lng"],
                status="normal",
                battery_pct=97.5,
                signal_strength=-60.0,
                mesh_level=pdata["level"],
                is_gateway=(pdata["level"] == 0),
                is_simulated=False,
                last_seen=datetime.utcnow(),
                api_key_hash=key_hash
            )
            db.add(node)
            snode = SensorNode(
                id=pdata["code"],
                name=pdata["name"],
                hazard_type=pdata["hazard_type"],
                latitude=pdata["lat"],
                longitude=pdata["lng"],
                status="ONLINE",
                parent_node_id=pdata["parent"],
                hop_count=pdata["level"],
                battery_pct=97.5,
                signal_rssi=-60.0,
                is_gateway=(pdata["level"] == 0),
                last_seen=datetime.utcnow()
            )
            db.add(snode)
            db.flush()
            created_nodes[pdata["code"]] = node
            print(f"  Node: {pdata['code']:<8} | Key: {plain_key}")

        # -------------------------------------------------------------
        # 2. Simulated Nodes (15 Nodes: GW-01 + NODE-01..NODE-14)
        # -------------------------------------------------------------
        simulated_nodes_data = [
            {"code": "GW-01", "name": "ASDMA State Disaster Ops Center (GSM Sink)", "hazard_type": "multi", "lat": 26.1450, "lng": 91.7360, "is_gw": True, "level": 0, "parent": None},
            {"code": "NODE-01", "name": "Saraighat Brahmaputra River Gauge", "hazard_type": "flood", "lat": 26.1860, "lng": 91.6980, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-02", "name": "Pandu Hydrological Monitoring Post", "hazard_type": "flood", "lat": 26.1800, "lng": 91.7120, "is_gw": False, "level": 2, "parent": "NODE-01"},
            {"code": "NODE-03", "name": "Kampur Town Kopili River Sensor", "hazard_type": "flood", "lat": 26.0520, "lng": 92.7750, "is_gw": False, "level": 3, "parent": "NODE-02"},
            {"code": "NODE-04", "name": "Raha Kopili Confluence Sentinel", "hazard_type": "flood", "lat": 26.2200, "lng": 92.5200, "is_gw": False, "level": 4, "parent": "NODE-03"},
            {"code": "NODE-05", "name": "Dharamtul Riverbed Telemetry Station", "hazard_type": "flood", "lat": 26.1500, "lng": 92.3500, "is_gw": False, "level": 5, "parent": "NODE-04"},
            {"code": "NODE-06", "name": "Palashbari Brahmaputra Embankment", "hazard_type": "flood", "lat": 26.1300, "lng": 91.5000, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-07", "name": "Sualkuchi North Bank Flood Watch", "hazard_type": "flood", "lat": 26.1700, "lng": 91.5700, "is_gw": False, "level": 2, "parent": "NODE-06"},
            {"code": "NODE-08", "name": "North Guwahati Hill Slope Sensor", "hazard_type": "landslide", "lat": 26.2100, "lng": 91.7200, "is_gw": False, "level": 2, "parent": "NODE-01"},
            {"code": "NODE-09", "name": "Sonapur Digaru River Sentry", "hazard_type": "flood", "lat": 26.1200, "lng": 91.9800, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-10", "name": "Morigaon Lowland Inundation Sensor", "hazard_type": "flood", "lat": 26.2500, "lng": 92.3400, "is_gw": False, "level": 2, "parent": "NODE-09"},
            {"code": "NODE-11", "name": "Guwahati Central AQI & Weather Post", "hazard_type": "air", "lat": 26.1850, "lng": 91.7500, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-12", "name": "GMCH Emergency Zone Sensor", "hazard_type": "air", "lat": 26.1550, "lng": 91.7700, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-13", "name": "Noonmati Refinery AQI Sentry", "hazard_type": "air", "lat": 26.1950, "lng": 91.8000, "is_gw": False, "level": 2, "parent": "NODE-12"},
            {"code": "NODE-14", "name": "Dispur Capital Complex Multi-Hazard", "hazard_type": "multi", "lat": 26.1400, "lng": 91.7900, "is_gw": False, "level": 2, "parent": "NODE-01"},
        ]

        sim_master_key = "ts_sim_master_key_2026"
        sim_key_hash = hash_key(sim_master_key)

        for sdata in simulated_nodes_data:
            node = Node(
                code=sdata["code"],
                name=sdata["name"],
                hazard_type=sdata["hazard_type"],
                latitude=sdata["lat"],
                longitude=sdata["lng"],
                status="normal",
                battery_pct=98.5,
                signal_strength=-52.0 - (sdata["level"] * 7),
                mesh_level=sdata["level"],
                is_gateway=sdata["is_gw"],
                is_simulated=True,
                last_seen=datetime.utcnow(),
                api_key_hash=sim_key_hash
            )
            db.add(node)
            snode = SensorNode(
                id=sdata["code"],
                name=sdata["name"],
                hazard_type=sdata["hazard_type"],
                latitude=sdata["lat"],
                longitude=sdata["lng"],
                status="GATEWAY" if sdata["is_gw"] else ("ONLINE" if sdata["level"] <= 1 else "MESH_RELAY"),
                parent_node_id=sdata["parent"],
                hop_count=sdata["level"],
                battery_pct=98.5,
                signal_rssi=-52.0 - (sdata["level"] * 7),
                is_gateway=sdata["is_gw"],
                last_seen=datetime.utcnow()
            )
            db.add(snode)
            db.flush()
            created_nodes[sdata["code"]] = node

        # Link parents
        for sdata in simulated_nodes_data:
            if sdata["parent"] and sdata["parent"] in created_nodes:
                created_nodes[sdata["code"]].parent_node_id = created_nodes[sdata["parent"]].id

        # -------------------------------------------------------------
        # 3. Mesh Links
        # -------------------------------------------------------------
        for sdata in simulated_nodes_data:
            if sdata["parent"] and sdata["parent"] in created_nodes:
                link = MeshLink(
                    from_node_id=created_nodes[sdata["code"]].id,
                    to_node_id=created_nodes[sdata["parent"]].id,
                    rssi=-54.0 - (sdata["level"] * 8),
                    link_type="cellular" if sdata["is_gw"] else ("lora" if sdata["level"] >= 3 else "esp_now"),
                    active=True
                )
                db.add(link)

        # -------------------------------------------------------------
        # 4. Assam Contacts & Safe Shelters (20+ Records)
        # -------------------------------------------------------------
        contacts_data = [
            {"name": "National Emergency Response Helpline", "category": "helpline", "phone": "112", "district": "All Assam", "cap": None, "occ": None, "lat": 26.1450, "lng": 91.7360},
            {"name": "ASDMA State Emergency Operation Centre (SEOC)", "category": "authority", "phone": "1070", "district": "Kamrup Metro (Dispur)", "cap": None, "occ": None, "lat": 26.1400, "lng": 91.7900},
            {"name": "DEOC Kamrup Metropolitan Control Room", "category": "authority", "phone": "1077", "district": "Guwahati", "cap": None, "occ": None, "lat": 26.1850, "lng": 91.7500},
            {"name": "DEOC Nagaon Flood Control Desk", "category": "authority", "phone": "03672-233222", "district": "Nagaon", "cap": None, "occ": None, "lat": 26.3450, "lng": 92.6850},
            {"name": "NDRF 1st Battalion Command HQ Patgaon", "category": "rescue", "phone": "+91 361 2840284", "district": "Kamrup Rural", "cap": None, "occ": None, "lat": 26.1100, "lng": 91.5900},
            {"name": "SDRF Assam Fire & Emergency Headquarters", "category": "rescue", "phone": "0361-2540222", "district": "Guwahati Panbazar", "cap": None, "occ": None, "lat": 26.1890, "lng": 91.7450},
            {"name": "Cotton Collegiate HS Evacuation Camp", "category": "shelter", "phone": "+91 361 2540111", "district": "Guwahati Central", "cap": 800, "occ": 210, "lat": 26.1870, "lng": 91.7480},
            {"name": "Kampur Higher Secondary School Relief Camp", "category": "shelter", "phone": "+91 3672 245100", "district": "Nagaon (Kampur)", "cap": 650, "occ": 420, "lat": 26.0530, "lng": 92.7760},
            {"name": "Raha College Flood Relief Center", "category": "shelter", "phone": "+91 3672 288300", "district": "Nagaon (Raha)", "cap": 500, "occ": 195, "lat": 26.2220, "lng": 92.5210},
            {"name": "GMCH Emergency Disaster Relief Wing", "category": "shelter", "phone": "+91 361 2130190", "district": "Guwahati", "cap": 400, "occ": 65, "lat": 26.1550, "lng": 91.7700},
            {"name": "Palashbari Relief Hall", "category": "shelter", "phone": "+91 361 2842100", "district": "Kamrup Rural", "cap": 450, "occ": 110, "lat": 26.1320, "lng": 91.5020},
            {"name": "Sualkuchi Community Center Shelter", "category": "shelter", "phone": "+91 361 2831200", "district": "Kamrup Rural", "cap": 350, "occ": 40, "lat": 26.1710, "lng": 91.5720},
            {"name": "Morigaon District Stadium Relief Camp", "category": "shelter", "phone": "+91 3678 240210", "district": "Morigaon", "cap": 700, "occ": 310, "lat": 26.2520, "lng": 92.3420},
            {"name": "Central Water Commission (CWC) Guwahati River Monitoring", "category": "authority", "phone": "0361-2260170", "district": "Guwahati", "cap": None, "occ": None, "lat": 26.1820, "lng": 91.7580},
            {"name": "Indian Red Cross Society Assam State Branch", "category": "ngo", "phone": "+91 361 2664538", "district": "Chandmari Guwahati", "cap": None, "occ": None, "lat": 26.1890, "lng": 91.7750},
            {"name": "Oxfam India Flood Relief Hub Guwahati", "category": "ngo", "phone": "+91 361 2459981", "district": "Kamrup Metro", "cap": None, "occ": None, "lat": 26.1750, "lng": 91.7650},
            {"name": "Brahmaputra Board River Engineering Command", "category": "authority", "phone": "0361-2300084", "district": "Basistha Guwahati", "cap": None, "occ": None, "lat": 26.1280, "lng": 91.7890},
            {"name": "Assam State Inland Water Transport (Rescue Boats)", "category": "rescue", "phone": "0361-2540193", "district": "Pandu Port", "cap": None, "occ": None, "lat": 26.1830, "lng": 91.7140},
            {"name": "Free 108 Emergency Ambulance Assam", "category": "helpline", "phone": "108", "district": "All Assam", "cap": None, "occ": None, "lat": 26.1500, "lng": 91.7500},
            {"name": "Fire & Emergency Services Assam (Panbazar)", "category": "helpline", "phone": "101", "district": "Kamrup Metro", "cap": None, "occ": None, "lat": 26.1880, "lng": 91.7460}
        ]

        for c in contacts_data:
            contact = Contact(
                name=c["name"],
                category=c["category"],
                phone=c["phone"],
                district=c["district"],
                capacity=c["cap"],
                occupancy=c["occ"],
                latitude=c["lat"],
                longitude=c["lng"]
            )
            db.add(contact)

            # Also seed into SafeShelter table if category is shelter
            if c["category"] == "shelter":
                shelter = SafeShelter(
                    name=c["name"],
                    shelter_type="RELIEF_CAMP",
                    latitude=c["lat"],
                    longitude=c["lng"],
                    capacity=c["cap"] or 500,
                    current_occupancy=c["occ"] or 0,
                    contact_number=c["phone"],
                    is_open=True
                )
                db.add(shelter)

        # -------------------------------------------------------------
        # 5. Assam Hazard Zones (GeoJSON Polygons)
        # -------------------------------------------------------------
        kopili_flood_poly = {
            "type": "Polygon",
            "coordinates": [[
                [92.65, 26.00],
                [92.85, 26.02],
                [92.82, 26.14],
                [92.50, 26.25],
                [92.45, 26.15],
                [92.65, 26.00]
            ]]
        }
        brahmaputra_poly = {
            "type": "Polygon",
            "coordinates": [[
                [91.48, 26.12],
                [91.75, 26.19],
                [91.85, 26.22],
                [91.80, 26.25],
                [91.50, 26.18],
                [91.48, 26.12]
            ]]
        }
        deepor_beel_poly = {
            "type": "Polygon",
            "coordinates": [[
                [91.63, 26.10],
                [91.69, 26.10],
                [91.69, 26.15],
                [91.63, 26.15],
                [91.63, 26.10]
            ]]
        }

        zones_data = [
            {"name": "Kopili River High-Risk Inundation Zone (Kampur-Raha Breach)", "hazard_type": "flood", "risk": "critical", "geom": kopili_flood_poly},
            {"name": "Brahmaputra Low-Lying Riverine Flood Plain (Pandu-Saraighat)", "hazard_type": "flood", "risk": "high", "geom": brahmaputra_poly},
            {"name": "Deepor Beel Urban Catchment Waterlogging Zone", "hazard_type": "flood", "risk": "medium", "geom": deepor_beel_poly}
        ]

        for z in zones_data:
            zone = HazardZone(
                name=z["name"],
                hazard_type=z["hazard_type"],
                risk_level=z["risk"],
                geom_geojson=json.dumps(z["geom"])
            )
            db.add(zone)

        # -------------------------------------------------------------
        # 6. News Bulletins (Assam 16 June Incident)
        # -------------------------------------------------------------
        news_data = [
            {"region": "Assam", "title": "16 June Flood Deluge: Kopili River Breaches Historic High Flood Level at Kampur", "summary": "Continuous torrential precipitation recorded at 184 mm. Water level in Kopili River reached 4.85m exceeding previous HFL of 4.75m. Over 15,000 residents moved to relief camps in Kampur and Raha.", "source": "Assam Disaster Management Authority (ASDMA)"},
            {"region": "Assam", "title": "Brahmaputra River Inundation Alert Issued for Pandu & Palashbari", "summary": "Ultrasonic water level telemetry at Saraighat indicates 1.6m rapid surge. NDRF 1st Bn deployed 8 inflatable motorboats for evacuation along low-lying river islands.", "source": "Central Water Commission (CWC)"},
            {"region": "Assam", "title": "TERRA SHIELD Decentralized Mesh Network Operational Across Flood Hit Panchayats", "summary": "Battery-backed ESP-NOW and LoRa mesh nodes deployed at Kampur and Raha providing zero-cellular early warnings to local Gaonburahs.", "source": "District Disaster Emergency Operations"},
            {"region": "Assam", "title": "Guwahati Municipal Corporation Activates Sump Pumps Across Bharalu & Deepor Beel", "summary": "Urban water logging mitigation teams on 24x7 rotation as monsoonal depression hovers over Brahmaputra valley.", "source": "Guwahati Municipal Corporation"}
        ]

        for n in news_data:
            news = NewsFlash(
                region=n["region"],
                title=n["title"],
                summary=n["summary"],
                source=n["source"]
            )
            db.add(news)

        # -------------------------------------------------------------
        # 7. Subscribers & Gaonburahs (Assam Panchayats)
        # -------------------------------------------------------------
        subscribers_data = [
            {"name": "Bhupen Saikia (Gaonburah)", "phone": "+919864012345", "role": "sarpanch", "lang": "hi", "village": "Kampur Town Panchayat", "lat": 26.0520, "lng": 92.7750, "r": 6.0},
            {"name": "Hemanta Deka (Gaonburah)", "phone": "+919864012346", "role": "sarpanch", "lang": "hi", "village": "Raha Kopili Ward", "lat": 26.2200, "lng": 92.5200, "r": 5.0},
            {"name": "Biren Das (Panchayat Head)", "phone": "+919864012347", "role": "sarpanch", "lang": "hi", "village": "Palashbari Riverbank", "lat": 26.1300, "lng": 91.5000, "r": 7.0},
            {"name": "Pranab Barman (Ward Councillor)", "phone": "+919864012348", "role": "councillor", "lang": "en", "village": "Pandu Port Colony", "lat": 26.1800, "lng": 91.7120, "r": 4.0},
            {"name": "Jonali Kalita (Citizen)", "phone": "+919864012349", "role": "citizen", "lang": "hi", "village": "Saraighat Ghat", "lat": 26.1860, "lng": 91.6980, "r": 4.0},
            {"name": "Ramen Bora (Citizen)", "phone": "+919864012350", "role": "citizen", "lang": "en", "village": "Dharamtul", "lat": 26.1500, "lng": 92.3500, "r": 5.0},
            {"name": "Mitali Hazarika (Citizen)", "phone": "+919864012351", "role": "citizen", "lang": "hi", "village": "Sualkuchi Silk Town", "lat": 26.1700, "lng": 91.5700, "r": 4.0},
            {"name": "Debajit Sarma (Citizen)", "phone": "+919864012352", "role": "citizen", "lang": "hi", "village": "Sonapur Digaru", "lat": 26.1200, "lng": 91.9800, "r": 5.0},
        ]

        for s in subscribers_data:
            sub = Subscriber(
                name=s["name"],
                whatsapp_number=s["phone"],
                role=s["role"],
                language=s["lang"],
                village=s["village"],
                latitude=s["lat"],
                longitude=s["lng"],
                radius_km=s["r"]
            )
            db.add(sub)

        # -------------------------------------------------------------
        # 8. Demo Users
        # -------------------------------------------------------------
        admin_user = User(
            email="admin@terrashield.gov.in",
            password_hash=hash_password("admin123"),
            role="authority"
        )
        viewer_user = User(
            email="viewer@terrashield.gov.in",
            password_hash=hash_password("viewer123"),
            role="viewer"
        )
        db.add(admin_user)
        db.add(viewer_user)

        # -------------------------------------------------------------
        # 9. Active Incident Alert & WhatsApp Verification (16 June Assam Flood)
        # -------------------------------------------------------------
        incident = IncidentAlert(
            hazard_type="FLOOD",
            severity="EMERGENCY",
            title="Kampur Kopili River Surge & Embankment Breach (16 June Assam Incident)",
            description="Continuous deluge has pushed River Kopili gauge to 4.85m at Kampur, breaching the Highest Flood Level (HFL 4.75m). Inundation threatens 12 villages across Kampur and Raha revenue circles.",
            location_name="Kampur, Kopili River Basin (Assam)",
            latitude=26.0500,
            longitude=92.7800,
            radius_km=15.0,
            timestamp=datetime.utcnow(),
            is_active=True,
            verified_by_human=True,
            verification_source="WhatsApp Gaonburah Verified (Bhupen Saikia)",
            evacuation_triggered=True,
            ndrf_dispatched=True
        )
        db.add(incident)
        db.flush()

        verif = WhatsAppVerification(
            incident_id=incident.id,
            sarpanch_name="Bhupen Saikia (Gaonburah - Kampur)",
            phone_number="+919864012345",
            query_sent="⚠️ *TERRA SHIELD आपदा चेतावनी प्रणाली*\n\nनमस्ते श्री भूपेन सैकिया जी (गांवबुढ़ा - कामपुर),\nसेंसर द्वारा *कामपुर कोपिली तटबंध* में जलस्तर 4.85m (HFL से ऊपर) दर्ज किया गया है।\n\nक्या कामपुर में बाढ़ का पानी गांवों में घुस रहा है? कृपया पुष्टि करें।",
            query_language="hi",
            response_received="हाँ, पानी तटबंध पार कर गांव में घुस रहा है। तुरंत राहत नाव भेजें।",
            verification_status="CONFIRMED",
            nlp_confidence=0.96,
            timestamp=datetime.utcnow()
        )
        db.add(verif)

        # Additional System Alert
        sys_alert = Alert(
            node_id=created_nodes["PHY-03"].id,
            hazard_type="flood",
            severity="critical",
            confidence=0.98,
            message="Kampur Embankment Gauge Critical - Kopili River Deluge (16 June Incident)",
            reason="Water level reading 4.85m exceeds extreme danger mark (4.75m HFL). Evacuation protocol active.",
            decided_on_device=True,
            decision_ms=35,
            status="open",
            ground_truth="confirmed",
            latitude=26.0800,
            longitude=92.7400,
            node_timestamp=datetime.utcnow(),
            received_at=datetime.utcnow()
        )
        db.add(sys_alert)

        # -------------------------------------------------------------
        # 10. Baseline Readings for all nodes
        # -------------------------------------------------------------
        for code, node in created_nodes.items():
            # Higher water levels for flood nodes
            is_flood_critical = code in ["PHY-01", "PHY-02", "PHY-03", "NODE-01", "NODE-03", "NODE-04"]
            reading = Reading(
                node_id=node.id,
                ts=datetime.utcnow(),
                water_level_cm=485.0 if code == "PHY-03" else (340.0 if is_flood_critical else 165.0),
                water_rate_cm_min=1.8 if is_flood_critical else 0.1,
                pm25=28.0,
                pm10=45.0,
                temperature_c=27.5,
                humidity=89.0,
                wind_speed=18.5,
                wind_dir=195.0,
                smoke_index=0.8,
                raw_bytes=2400,
                tx_bytes=128
            )
            db.add(reading)

            t_record = TelemetryRecord(
                node_id=code,
                timestamp=datetime.utcnow(),
                water_level_m=4.85 if code in ["PHY-02", "PHY-03", "NODE-03"] else (3.40 if is_flood_critical else 1.65),
                water_rate_of_change=1.8 if is_flood_critical else 0.05,
                temperature_c=27.5,
                humidity_pct=89.0,
                wind_speed_kmh=18.5,
                wind_direction_deg=195.0,
                pm25=28.0,
                pm10=45.0,
                mesh_hops=node.mesh_level
            )
            db.add(t_record)

        db.commit()
        print("\nAssam 16 June Incident Database seeded successfully!")
        print(f"  Total Nodes: {len(created_nodes)} (5 Physical + 15 Simulated)")
        print(f"  Contacts & Shelters: {len(contacts_data)}")
        print(f"  Hazard Zones: {len(zones_data)}")
        print(f"  Subscribers: {len(subscribers_data)}")
        print("  Demo Users:")
        print("    Authority : admin@terrashield.gov.in / admin123")
        print("    Viewer    : viewer@terrashield.gov.in / viewer123")
        print(f"  Sim Master Key : {sim_master_key}")
        print("=================================================================\n")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    force_run = "--force" in sys.argv or "-f" in sys.argv
    seed_database(force=force_run)
