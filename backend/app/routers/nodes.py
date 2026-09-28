from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import SensorNode, SafeShelter
from app.schemas import SensorNodeResponse, MeshTopologyResponse
from app.mesh_manager import mesh_manager
from app.websocket_manager import ws_manager
from app.config import settings

router = APIRouter(prefix="/nodes", tags=["Nodes & Mesh"])

@router.get("", response_model=List[SensorNodeResponse])
def get_all_nodes(db: Session = Depends(get_db)):
    """Returns all registered sensor nodes and their current health/mesh status."""
    return db.query(SensorNode).all()

@router.get("/topology", response_model=MeshTopologyResponse)
def get_mesh_topology(db: Session = Depends(get_db)):
    """Returns the live dynamic mesh topology graph with node hops and parent links."""
    return mesh_manager.get_topology(db)

@router.post("/blackout", response_model=dict)
async def toggle_blackout(active: bool, db: Session = Depends(get_db)):
    """
    Simulates total cellular tower collapse during severe disaster.
    Demonstrates decentralized multi-hop mesh failover.
    """
    status = mesh_manager.toggle_cellular_blackout(db, active)
    
    # Broadcast network state change over WebSockets
    await ws_manager.broadcast("NETWORK_STATE_CHANGE", {
        "cellular_blackout": status,
        "mode": "DECENTRALIZED_MESH_BLACKOUT" if status else "HYBRID_CELLULAR"
    })

    return {
        "cellular_blackout": status,
        "mode": "DECENTRALIZED_MESH_BLACKOUT" if status else "HYBRID_CELLULAR",
        "message": "Mesh failover active! Packets rerouted to emergency local LoRa/Satellite sink." if status else "Cellular infrastructure restored."
    }

@router.post("/seed", response_model=dict)
def seed_default_nodes_and_shelters(db: Session = Depends(get_db)):
    """Seeds 15 realistic edge nodes across the catchment area + 4 safe evacuation shelters."""
    if db.query(SensorNode).count() > 0:
        return {"status": "already_seeded", "node_count": db.query(SensorNode).count()}

    # Base coords: Brahmaputra & Kopili River Basin, Assam (16 June Incident)
    base_lat = settings.DEFAULT_LAT
    base_lng = settings.DEFAULT_LNG

    nodes_data = [
        # Physical Hardware Sentinels (PHY-01 to PHY-05)
        {"id": "PHY-01", "name": "Saraighat Brahmaputra River Sentry (Hardware)", "hazard_type": "flood", "lat": 26.1850, "lng": 91.7000, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "PHY-02", "name": "Kopili River Bridge Inundation Gauge (Hardware)", "hazard_type": "flood", "lat": 26.0500, "lng": 92.7800, "is_gw": False, "hops": 2, "parent": "PHY-01"},
        {"id": "PHY-03", "name": "Kampur Embankment Critical Sentry (Hardware)", "hazard_type": "flood", "lat": 26.0800, "lng": 92.7400, "is_gw": False, "hops": 3, "parent": "PHY-02"},
        {"id": "PHY-04", "name": "Deepor Beel Catchment Water Watch (Hardware)", "hazard_type": "flood", "lat": 26.1200, "lng": 91.6600, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "PHY-05", "name": "Pandu Port Hydrological Telemetry Post (Hardware)", "hazard_type": "flood", "lat": 26.1820, "lng": 91.7150, "is_gw": False, "hops": 1, "parent": "GW-01"},

        # Gateway 1 (ASDMA State Disaster Ops Center)
        {"id": "GW-01", "name": "ASDMA State Disaster Ops Center (GSM Sink)", "hazard_type": "multi", "lat": 26.1450, "lng": 91.7360, "is_gw": True, "hops": 0, "parent": None},
        
        # River Flood Catchment Sensor Nodes (Assam 16 June Incident Corridor)
        {"id": "NODE-01", "name": "Saraighat Brahmaputra River Gauge", "hazard_type": "flood", "lat": 26.1860, "lng": 91.6980, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-02", "name": "Pandu Hydrological Monitoring Post", "hazard_type": "flood", "lat": 26.1800, "lng": 91.7120, "is_gw": False, "hops": 2, "parent": "NODE-01"},
        {"id": "NODE-03", "name": "Kampur Town Kopili River Sensor", "hazard_type": "flood", "lat": 26.0520, "lng": 92.7750, "is_gw": False, "hops": 3, "parent": "NODE-02"},
        {"id": "NODE-04", "name": "Raha Kopili Confluence Sentinel", "hazard_type": "flood", "lat": 26.2200, "lng": 92.5200, "is_gw": False, "hops": 4, "parent": "NODE-03"},
        {"id": "NODE-05", "name": "Dharamtul Riverbed Telemetry Station", "hazard_type": "flood", "lat": 26.1500, "lng": 92.3500, "is_gw": False, "hops": 5, "parent": "NODE-04"},
        {"id": "NODE-06", "name": "Palashbari Brahmaputra Embankment", "hazard_type": "flood", "lat": 26.1300, "lng": 91.5000, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-07", "name": "Sualkuchi North Bank Flood Watch", "hazard_type": "flood", "lat": 26.1700, "lng": 91.5700, "is_gw": False, "hops": 2, "parent": "NODE-06"},
        {"id": "NODE-08", "name": "North Guwahati Hill Slope Sensor", "hazard_type": "landslide", "lat": 26.2100, "lng": 91.7200, "is_gw": False, "hops": 2, "parent": "NODE-01"},
        {"id": "NODE-09", "name": "Sonapur Digaru River Sentry", "hazard_type": "flood", "lat": 26.1200, "lng": 91.9800, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-10", "name": "Morigaon Lowland Inundation Sensor", "hazard_type": "flood", "lat": 26.2500, "lng": 92.3400, "is_gw": False, "hops": 2, "parent": "NODE-09"},
        
        # Urban & Industrial Sentinels
        {"id": "NODE-11", "name": "Guwahati Central AQI & Weather Post", "hazard_type": "air", "lat": 26.1850, "lng": 91.7500, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-12", "name": "GMCH Emergency Zone Sensor", "hazard_type": "air", "lat": 26.1550, "lng": 91.7700, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-13", "name": "Noonmati Refinery AQI Sentry", "hazard_type": "air", "lat": 26.1950, "lng": 91.8000, "is_gw": False, "hops": 2, "parent": "NODE-12"},
        {"id": "NODE-14", "name": "Dispur Capital Complex Multi-Hazard", "hazard_type": "multi", "lat": 26.1400, "lng": 91.7900, "is_gw": False, "hops": 2, "parent": "NODE-01"},
    ]

    for nd in nodes_data:
        node = SensorNode(
            id=nd["id"],
            name=nd["name"],
            hazard_type=nd["hazard_type"],
            latitude=nd["lat"],
            longitude=nd["lng"],
            status="GATEWAY" if nd["is_gw"] else ("ONLINE" if nd["hops"] <= 1 else "MESH_RELAY"),
            parent_node_id=nd["parent"],
            hop_count=nd["hops"],
            battery_pct=96.0,
            signal_rssi=-54.0 - (nd["hops"] * 8),
            is_gateway=nd["is_gw"]
        )
        db.add(node)

    # Assam Evacuation Shelters & Relief Camps
    shelters_data = [
        {"name": "Cotton Collegiate HS Evacuation Camp", "type": "SHELTER", "lat": 26.1870, "lng": 91.7480, "capacity": 800, "occupancy": 210},
        {"name": "Kampur Higher Secondary School Relief Camp", "type": "RELIEF_CAMP", "lat": 26.0530, "lng": 92.7760, "capacity": 650, "occupancy": 420},
        {"name": "Raha College Flood Relief Center", "type": "RELIEF_CAMP", "lat": 26.2220, "lng": 92.5210, "capacity": 500, "occupancy": 195},
        {"name": "GMCH Emergency Disaster Relief Wing", "type": "HOSPITAL", "lat": 26.1550, "lng": 91.7700, "capacity": 400, "occupancy": 65},
        {"name": "Palashbari Relief Hall", "type": "SHELTER", "lat": 26.1320, "lng": 91.5020, "capacity": 450, "occupancy": 110},
    ]

    for sd in shelters_data:
        shelter = SafeShelter(
            name=sd["name"],
            shelter_type=sd["type"],
            latitude=sd["lat"],
            longitude=sd["lng"],
            capacity=sd["capacity"],
            current_occupancy=sd["occupancy"],
            contact_number="+91 1070 (ASDMA Toll Free)",
            is_open=True
        )
        db.add(shelter)

    db.commit()
    return {"status": "seeded", "nodes": len(nodes_data), "shelters": len(shelters_data)}
