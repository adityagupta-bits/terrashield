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
    WeatherForecast, NewsFlash, User, MeshLink
)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def seed_database():
    db = SessionLocal()
    try:
        print("=================================================================")
        print("  TERRA SHIELD (SIH26178) - Database Seeding Engine")
        print("=================================================================")

        # Check if already seeded
        if db.query(Node).count() > 0:
            print("Database already contains nodes. Skipping full reseeding.")
            return

        base_lat = 30.0869
        base_lng = 78.2676

        # -------------------------------------------------------------
        # 1. Physical Sensor Nodes (PHY-01 to PHY-05)
        # -------------------------------------------------------------
        physical_keys = {}
        physical_nodes_data = [
            {"code": "PHY-01", "name": "Ganga Barrage Acoustic Sentry (Hardware)", "hazard_type": "flood", "lat": base_lat + 0.008, "lng": base_lng - 0.006, "level": 1, "parent": None},
            {"code": "PHY-02", "name": "Chandrabhaga River Bridge (Hardware)", "hazard_type": "flood", "lat": base_lat + 0.019, "lng": base_lng - 0.012, "level": 2, "parent": "PHY-01"},
            {"code": "PHY-03", "name": "Shivpuri Rafting Ghat Gauge (Hardware)", "hazard_type": "flood", "lat": base_lat + 0.041, "lng": base_lng + 0.018, "level": 3, "parent": "PHY-02"},
            {"code": "PHY-04", "name": "Chilla Forest Thermal Sentinel (Hardware)", "hazard_type": "fire", "lat": base_lat - 0.031, "lng": base_lng - 0.024, "level": 1, "parent": None},
            {"code": "PHY-05", "name": "Triveni Ghat Smart AQI Post (Hardware)", "hazard_type": "air", "lat": base_lat + 0.003, "lng": base_lng - 0.004, "level": 1, "parent": None},
        ]

        print("\n--- GENERATING PHYSICAL HARDWARE API KEYS (STORE SECURELY) ---")
        created_nodes = {}

        for pdata in physical_nodes_data:
            plain_key = f"ts_live_{pdata['code'].lower()}_{secrets.token_hex(12)}"
            key_hash = hash_key(plain_key)
            physical_keys[pdata["code"]] = plain_key

            node = Node(
                code=pdata["code"],
                name=pdata["name"],
                hazard_type=pdata["hazard_type"],
                latitude=pdata["lat"],
                longitude=pdata["lng"],
                status="normal",
                battery_pct=96.5,
                signal_strength=-62.0,
                mesh_level=pdata["level"],
                is_gateway=(pdata["level"] == 0),
                is_simulated=False,
                last_seen=datetime.utcnow(),
                api_key_hash=key_hash
            )
            db.add(node)
            db.flush()
            created_nodes[pdata["code"]] = node
            print(f"  Node: {pdata['code']:<8} | Key: {plain_key}")

        # -------------------------------------------------------------
        # 2. Simulated Nodes (15 Nodes: GW-01 + NODE-01..NODE-14)
        # -------------------------------------------------------------
        simulated_nodes_data = [
            {"code": "GW-01", "name": "Main Control Station (GSM Sink)", "hazard_type": "multi", "lat": base_lat, "lng": base_lng, "is_gw": True, "level": 0, "parent": None},
            {"code": "NODE-01", "name": "Ganga Barrage River Gauge", "hazard_type": "flood", "lat": base_lat + 0.012, "lng": base_lng - 0.008, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-02", "name": "Chandrabhaga Confluence Sensor", "hazard_type": "flood", "lat": base_lat + 0.024, "lng": base_lng - 0.015, "is_gw": False, "level": 2, "parent": "NODE-01"},
            {"code": "NODE-03", "name": "Shivpuri Upstream Gauge", "hazard_type": "flood", "lat": base_lat + 0.045, "lng": base_lng + 0.022, "is_gw": False, "level": 3, "parent": "NODE-02"},
            {"code": "NODE-04", "name": "Byasi Canyon Flood Sentinel", "hazard_type": "flood", "lat": base_lat + 0.065, "lng": base_lng + 0.038, "is_gw": False, "level": 4, "parent": "NODE-03"},
            {"code": "NODE-05", "name": "Devprayag Confluence Watch", "hazard_type": "flood", "lat": base_lat + 0.095, "lng": base_lng + 0.055, "is_gw": False, "level": 5, "parent": "NODE-04"},
            {"code": "NODE-06", "name": "Rajaji National Park Sector 1", "hazard_type": "fire", "lat": base_lat - 0.025, "lng": base_lng - 0.020, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-07", "name": "Chilla Forest Thermal Sentry", "hazard_type": "fire", "lat": base_lat - 0.042, "lng": base_lng - 0.035, "is_gw": False, "level": 2, "parent": "NODE-06"},
            {"code": "NODE-08", "name": "Kaudiyala Ridge (LoRa Satellite Backup)", "hazard_type": "fire", "lat": base_lat + 0.050, "lng": base_lng + 0.040, "is_gw": False, "level": 2, "parent": "NODE-03"},
            {"code": "NODE-09", "name": "Neelkanth Valley Fire Lookout", "hazard_type": "fire", "lat": base_lat - 0.018, "lng": base_lng + 0.030, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-10", "name": "Manikoot Ridge Acoustic Node", "hazard_type": "fire", "lat": base_lat - 0.035, "lng": base_lng + 0.045, "is_gw": False, "level": 2, "parent": "NODE-09"},
            {"code": "NODE-11", "name": "Triveni Ghat Public AQI Node", "hazard_type": "air", "lat": base_lat + 0.005, "lng": base_lng - 0.005, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-12", "name": "AIIMS Rishikesh Health Zone Node", "hazard_type": "air", "lat": base_lat - 0.020, "lng": base_lng + 0.010, "is_gw": False, "level": 1, "parent": "GW-01"},
            {"code": "NODE-13", "name": "IDPL Industrial Area AQI Sentry", "hazard_type": "air", "lat": base_lat - 0.015, "lng": base_lng - 0.015, "is_gw": False, "level": 2, "parent": "NODE-12"},
            {"code": "NODE-14", "name": "Tapovan Tourist Belt Multi-Hazard", "hazard_type": "multi", "lat": base_lat + 0.030, "lng": base_lng + 0.015, "is_gw": False, "level": 2, "parent": "NODE-01"},
        ]

        # Universal simulator master key
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
                battery_pct=98.0,
                signal_strength=-50.0 - (sdata["level"] * 8),
                mesh_level=sdata["level"],
                is_gateway=sdata["is_gw"],
                is_simulated=True,
                last_seen=datetime.utcnow(),
                api_key_hash=sim_key_hash
            )
            db.add(node)
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
                    rssi=-52.0 - (sdata["level"] * 9),
                    link_type="cellular" if sdata["is_gw"] else ("lora" if sdata["level"] >= 3 else "esp_now"),
                    active=True
                )
                db.add(link)

        # -------------------------------------------------------------
        # 4. Contacts (20+ Contacts)
        # -------------------------------------------------------------
        contacts_data = [
            {"name": "National Emergency Response Helpline", "category": "helpline", "phone": "112", "district": "All Districts", "cap": None, "occ": None, "lat": base_lat, "lng": base_lng},
            {"name": "NDRF 8th Battalion Control HQ", "category": "rescue", "phone": "+91 11 24363260", "district": "Dehradun", "cap": None, "occ": None, "lat": base_lat + 0.015, "lng": base_lng + 0.020},
            {"name": "SDRF Uttarakhand Rapid Disaster Command", "category": "rescue", "phone": "+91 135 2710334", "district": "Tehri Garhwal", "cap": None, "occ": None, "lat": base_lat + 0.022, "lng": base_lng - 0.010},
            {"name": "Fire Service Control Room", "category": "helpline", "phone": "101", "district": "Rishikesh", "cap": None, "occ": None, "lat": base_lat + 0.002, "lng": base_lng - 0.002},
            {"name": "Ambulance Emergency Medical Response", "category": "helpline", "phone": "108", "district": "Uttarakhand State", "cap": None, "occ": None, "lat": base_lat - 0.001, "lng": base_lng + 0.001},
            {"name": "District Emergency Operation Centre (DEOC)", "category": "authority", "phone": "1077", "district": "Dehradun", "cap": None, "occ": None, "lat": base_lat - 0.012, "lng": base_lng + 0.008},
            {"name": "Tehri Garhwal Flood Control Room", "category": "authority", "phone": "+91 1376 232155", "district": "Tehri Garhwal", "cap": None, "occ": None, "lat": base_lat + 0.035, "lng": base_lng + 0.025},
            {"name": "AIIMS Emergency Disaster Relief Wing", "category": "shelter", "phone": "+91 135 2462999", "district": "Rishikesh", "cap": 300, "occ": 42, "lat": base_lat - 0.019, "lng": base_lng + 0.012},
            {"name": "Government Inter College Evacuation Shelter", "category": "shelter", "phone": "+91 135 2430111", "district": "Rishikesh", "cap": 600, "occ": 85, "lat": base_lat + 0.008, "lng": base_lng + 0.005},
            {"name": "Panchayat Bhavan High-Ground Relief Camp", "category": "shelter", "phone": "+91 135 2439888", "district": "Shivpuri Sector", "cap": 450, "occ": 30, "lat": base_lat + 0.032, "lng": base_lng - 0.002},
            {"name": "Shri Bharat Mandir Community Relief Hall", "category": "shelter", "phone": "+91 135 2430222", "district": "Rishikesh Central", "cap": 500, "occ": 15, "lat": base_lat + 0.010, "lng": base_lng - 0.010},
            {"name": "Muni Ki Reti Disaster Relief Shelter", "category": "shelter", "phone": "+91 135 2430444", "district": "Tehri Garhwal", "cap": 400, "occ": 10, "lat": base_lat + 0.018, "lng": base_lng - 0.008},
            {"name": "Tapovan Primary School Evacuation Center", "category": "shelter", "phone": "+91 135 2430555", "district": "Tehri Garhwal", "cap": 350, "occ": 5, "lat": base_lat + 0.028, "lng": base_lng + 0.014},
            {"name": "Byasi High School Emergency Shelter", "category": "shelter", "phone": "+91 1378 245100", "district": "Tehri Garhwal", "cap": 250, "occ": 0, "lat": base_lat + 0.062, "lng": base_lng + 0.036},
            {"name": "Devprayag Sangam Community Center", "category": "shelter", "phone": "+91 1378 261200", "district": "Tehri Garhwal", "cap": 300, "occ": 0, "lat": base_lat + 0.092, "lng": base_lng + 0.052},
            {"name": "Indian Red Cross Society Uttarakhand Cell", "category": "ngo", "phone": "+91 135 2652155", "district": "Dehradun", "cap": None, "occ": None, "lat": base_lat - 0.015, "lng": base_lng + 0.018},
            {"name": "Sewa International Humanitarian Relief", "category": "ngo", "phone": "+91 135 2439120", "district": "Garhwal Division", "cap": None, "occ": None, "lat": base_lat + 0.005, "lng": base_lng + 0.022},
            {"name": "Goonj Disaster Relief & Clothing Bank", "category": "ngo", "phone": "+91 11 26972351", "district": "Rishikesh", "cap": None, "occ": None, "lat": base_lat - 0.008, "lng": base_lng - 0.015},
            {"name": "Rajaji National Park Range Officer (Fire Unit)", "category": "authority", "phone": "+91 135 2430777", "district": "Chilla Range", "cap": None, "occ": None, "lat": base_lat - 0.035, "lng": base_lng - 0.030},
            {"name": "Kaudiyala Emergency Relief Station", "category": "rescue", "phone": "+91 1378 245200", "district": "Tehri Garhwal", "cap": 150, "occ": 12, "lat": base_lat + 0.052, "lng": base_lng + 0.042},
            {"name": "State Disaster Mitigation & Management Centre", "category": "authority", "phone": "+91 135 2710335", "district": "Dehradun", "cap": None, "occ": None, "lat": base_lat - 0.025, "lng": base_lng + 0.005}
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

        # -------------------------------------------------------------
        # 5. Hazard Zones (GeoJSON Polygons)
        # -------------------------------------------------------------
        flood_poly = {
            "type": "Polygon",
            "coordinates": [[
                [base_lng - 0.020, base_lat + 0.005],
                [base_lng - 0.015, base_lat + 0.035],
                [base_lng + 0.030, base_lat + 0.055],
                [base_lng + 0.045, base_lat + 0.040],
                [base_lng + 0.010, base_lat + 0.010],
                [base_lng - 0.020, base_lat + 0.005]
            ]]
        }
        fire_poly = {
            "type": "Polygon",
            "coordinates": [[
                [base_lng - 0.040, base_lat - 0.045],
                [base_lng - 0.020, base_lat - 0.020],
                [base_lng - 0.010, base_lat - 0.035],
                [base_lng - 0.030, base_lat - 0.055],
                [base_lng - 0.040, base_lat - 0.045]
            ]]
        }
        smog_poly = {
            "type": "Polygon",
            "coordinates": [[
                [base_lng - 0.025, base_lat - 0.025],
                [base_lng + 0.015, base_lat - 0.025],
                [base_lng + 0.015, base_lat + 0.015],
                [base_lng - 0.025, base_lat + 0.015],
                [base_lng - 0.025, base_lat - 0.025]
            ]]
        }

        zones_data = [
            {"name": "Ganga-Chandrabhaga High-Risk Inundation Zone", "hazard_type": "flood", "risk": "critical", "geom": flood_poly},
            {"name": "Chilla Forest & Rajaji Thermal Hotspot Belt", "hazard_type": "fire", "risk": "high", "geom": fire_poly},
            {"name": "IDPL-Triveni Urban Smog Dispersion Basin", "hazard_type": "air", "risk": "medium", "geom": smog_poly}
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
        # 6. News Bulletins
        # -------------------------------------------------------------
        news_data = [
            {"region": "Uttarakhand", "title": "NDMA Issues Cloudburst & Flash Flood Alert for Alaknanda-Bhagirathi Basin", "summary": "Heavy monsoonal precipitation projected across upper Garhwal catchment. All district disaster units placed on standby.", "source": "NDMA National Portal"},
            {"region": "Kerala", "title": "Wayanad Landslide Recovery: SDRF & TERRA SHIELD Mesh Deployed for Offline Comms", "summary": "Decentralized sensor beacons installed across vulnerable tea estate slopes after cellular infrastructure washouts.", "source": "Press Information Bureau"},
            {"region": "Assam", "title": "Brahmaputra Surpasses High Flood Level at Kaziranga Outpost", "summary": "Ultrasonic water level telemetry indicates 1.2m rise in 12 hours. Early warning bulletins sent to 14 Gram Panchayats.", "source": "Assam Disaster Management Authority"},
            {"region": "Himachal Pradesh", "title": "Wildfire Warning Raised Across Pine Belts Following Heat Anomaly", "summary": "High FFDI indices observed in Solan and Mandi districts; community fire sentries alerted.", "source": "HP Forest Department"}
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
        # 7. Subscribers (WhatsApp Verification & Citizen Alerting)
        # -------------------------------------------------------------
        subscribers_data = [
            {"name": "Ram Singh (Gram Pradhan)", "phone": "+919876543210", "role": "sarpanch", "lang": "hi", "village": "Shivpuri", "lat": base_lat + 0.045, "lng": base_lng + 0.022, "r": 6.0},
            {"name": "Suresh Rawat (Sarpanch)", "phone": "+919876543211", "role": "sarpanch", "lang": "hi", "village": "Byasi", "lat": base_lat + 0.065, "lng": base_lng + 0.038, "r": 5.0},
            {"name": "Kavita Devi (Panchayat Head)", "phone": "+919876543212", "role": "sarpanch", "lang": "hi", "village": "Chilla", "lat": base_lat - 0.042, "lng": base_lng - 0.035, "r": 8.0},
            {"name": "Anil Bhatt (Ward Councillor)", "phone": "+919876543213", "role": "councillor", "lang": "en", "village": "Triveni Ghat Ward 4", "lat": base_lat + 0.005, "lng": base_lng - 0.005, "r": 3.0},
            {"name": "Pooja Negi (Citizen)", "phone": "+919876543214", "role": "citizen", "lang": "hi", "village": "Tapovan", "lat": base_lat + 0.030, "lng": base_lng + 0.015, "r": 5.0},
            {"name": "Vikram Thapa (Citizen)", "phone": "+919876543215", "role": "citizen", "lang": "en", "village": "Muni Ki Reti", "lat": base_lat + 0.018, "lng": base_lng - 0.008, "r": 4.0},
            {"name": "Manoj Joshi (Citizen)", "phone": "+919876543216", "role": "citizen", "lang": "hi", "village": "Chandrabhaga Basti", "lat": base_lat + 0.024, "lng": base_lng - 0.015, "r": 4.0},
            {"name": "Deepak Pant (Citizen)", "phone": "+919876543217", "role": "citizen", "lang": "hi", "village": "IDPL Colony", "lat": base_lat - 0.015, "lng": base_lng - 0.015, "r": 5.0},
            {"name": "Meena Gusain (Citizen)", "phone": "+919876543218", "role": "citizen", "lang": "hi", "village": "Kaudiyala", "lat": base_lat + 0.050, "lng": base_lng + 0.040, "r": 6.0},
            {"name": "Rajesh Semwal (Citizen)", "phone": "+919876543219", "role": "citizen", "lang": "hi", "village": "Devprayag Confluence", "lat": base_lat + 0.095, "lng": base_lng + 0.055, "r": 6.0}
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
        # 8. Demo Users (Authorities & Viewers)
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
        # 9. Baseline Readings for all nodes
        # -------------------------------------------------------------
        for code, node in created_nodes.items():
            reading = Reading(
                node_id=node.id,
                ts=datetime.utcnow(),
                water_level_cm=165.0,
                water_rate_cm_min=0.2,
                pm25=42.0,
                pm10=65.0,
                temperature_c=26.5,
                humidity=58.0,
                wind_speed=11.2,
                wind_dir=45.0,
                smoke_index=2.1,
                raw_bytes=2400,
                tx_bytes=128
            )
            db.add(reading)

        db.commit()
        print("\nDatabase seeded successfully!")
        print(f"  Total Nodes: {len(created_nodes)} (5 Physical + 15 Simulated)")
        print(f"  Contacts: {len(contacts_data)}")
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
    seed_database()
