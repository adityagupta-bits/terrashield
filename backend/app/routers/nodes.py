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

    # Base coords: Rishikesh / Ganga - Chandrabhaga River Basin
    base_lat = settings.DEFAULT_LAT
    base_lng = settings.DEFAULT_LNG

    nodes_data = [
        # Gateway 1 (Cellular Uplink Node at Emergency Control HQ)
        {"id": "GW-01", "name": "Main Control Station (GSM Sink)", "hazard_type": "multi", "lat": base_lat, "lng": base_lng, "is_gw": True, "hops": 0, "parent": None},
        
        # River Flood Catchment Sensor Nodes
        {"id": "NODE-01", "name": "Ganga Barrage River Gauge", "hazard_type": "flood", "lat": base_lat + 0.012, "lng": base_lng - 0.008, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-02", "name": "Chandrabhaga Confluence Sensor", "hazard_type": "flood", "lat": base_lat + 0.024, "lng": base_lng - 0.015, "is_gw": False, "hops": 2, "parent": "NODE-01"},
        {"id": "NODE-03", "name": "Shivpuri Upstream Gauge", "hazard_type": "flood", "lat": base_lat + 0.045, "lng": base_lng + 0.022, "is_gw": False, "hops": 3, "parent": "NODE-02"},
        {"id": "NODE-04", "name": "Byasi Canyon Flood Sentinel", "hazard_type": "flood", "lat": base_lat + 0.065, "lng": base_lng + 0.038, "is_gw": False, "hops": 4, "parent": "NODE-03"},
        {"id": "NODE-05", "name": "Devprayag Confluence Watch", "hazard_type": "flood", "lat": base_lat + 0.095, "lng": base_lng + 0.055, "is_gw": False, "hops": 5, "parent": "NODE-04"},
        
        # Forest Fire Monitoring Edge Nodes (Chilla / Rajaji Forest Range)
        {"id": "NODE-06", "name": "Rajaji National Park Sector 1", "hazard_type": "fire", "lat": base_lat - 0.025, "lng": base_lng - 0.020, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-07", "name": "Chilla Forest Thermal Sentry", "hazard_type": "fire", "lat": base_lat - 0.042, "lng": base_lng - 0.035, "is_gw": False, "hops": 2, "parent": "NODE-06"},
        {"id": "NODE-08", "name": "Kaudiyala Ridge (LoRa Satellite Backup)", "hazard_type": "fire", "lat": base_lat + 0.050, "lng": base_lng + 0.040, "is_gw": False, "hops": 2, "parent": "NODE-03"},
        {"id": "NODE-09", "name": "Neelkanth Valley Fire Lookout", "hazard_type": "fire", "lat": base_lat - 0.018, "lng": base_lng + 0.030, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-10", "name": "Manikoot Ridge Acoustic Node", "hazard_type": "fire", "lat": base_lat - 0.035, "lng": base_lng + 0.045, "is_gw": False, "hops": 2, "parent": "NODE-09"},
        
        # Air Quality & Urban Smog Sentry Nodes
        {"id": "NODE-11", "name": "Triveni Ghat Public AQI Node", "hazard_type": "pollution", "lat": base_lat + 0.005, "lng": base_lng - 0.005, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-12", "name": "AIIMS Rishikesh Health Zone Node", "hazard_type": "pollution", "lat": base_lat - 0.020, "lng": base_lng + 0.010, "is_gw": False, "hops": 1, "parent": "GW-01"},
        {"id": "NODE-13", "name": "IDPL Industrial Area AQI Sentry", "hazard_type": "pollution", "lat": base_lat - 0.015, "lng": base_lng - 0.015, "is_gw": False, "hops": 2, "parent": "NODE-12"},
        {"id": "NODE-14", "name": "Tapovan Tourist Belt Multi-Hazard", "hazard_type": "multi", "lat": base_lat + 0.030, "lng": base_lng + 0.015, "is_gw": False, "hops": 2, "parent": "NODE-01"},
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
            battery_pct=95.0,
            signal_rssi=-55.0 - (nd["hops"] * 10),
            is_gateway=nd["is_gw"]
        )
        db.add(node)

    # Evacuation Shelters & Relief Camps
    shelters_data = [
        {"name": "Government Inter College Evacuation Shelter", "type": "SHELTER", "lat": base_lat + 0.008, "lng": base_lng + 0.005, "capacity": 600, "occupancy": 45},
        {"name": "AIIMS Emergency Disaster Relief Wing", "type": "HOSPITAL", "lat": base_lat - 0.019, "lng": base_lng + 0.012, "capacity": 300, "occupancy": 80},
        {"name": "Panchayat Bhavan High-Ground Relief Camp", "type": "RELIEF_CAMP", "lat": base_lat + 0.032, "lng": base_lng - 0.002, "capacity": 450, "occupancy": 20},
        {"name": "Shri Bharat Mandir Relief Community Hall", "type": "SHELTER", "lat": base_lat + 0.010, "lng": base_lng - 0.010, "capacity": 500, "occupancy": 10},
    ]

    for sd in shelters_data:
        shelter = SafeShelter(
            name=sd["name"],
            shelter_type=sd["type"],
            latitude=sd["lat"],
            longitude=sd["lng"],
            capacity=sd["capacity"],
            current_occupancy=sd["occupancy"],
            contact_number="+91 1070 (Toll Free)",
            is_open=True
        )
        db.add(shelter)

    db.commit()
    return {"status": "seeded", "nodes": len(nodes_data), "shelters": len(shelters_data)}
