from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.nodes import Node
from app.models.mesh import MeshLink
from app.mesh_manager import mesh_manager
from app.websocket_manager import ws_manager

router = APIRouter(prefix="/mesh", tags=["Mesh Network Topology"])

@router.get("/topology", response_model=dict)
def get_mesh_topology(db: Session = Depends(get_db)):
    """Returns dynamic multi-hop mesh graph with link RSSI, link types, and active backup sink status."""
    nodes = db.query(Node).all()
    links = db.query(MeshLink).filter(MeshLink.active == True).all()

    node_dict = {n.id: n for n in nodes}
    active_gateways = 0
    total_hops = 0

    node_list = []
    for n in nodes:
        if n.is_gateway and n.status != "offline":
            active_gateways += 1
        total_hops += n.mesh_level

        node_list.append({
            "id": n.id,
            "code": n.code,
            "name": n.name,
            "hazard_type": n.hazard_type,
            "latitude": n.latitude,
            "longitude": n.longitude,
            "status": n.status,
            "battery_pct": n.battery_pct,
            "signal_strength": n.signal_strength,
            "mesh_level": n.mesh_level,
            "is_gateway": n.is_gateway,
            "is_simulated": n.is_simulated,
            "is_backup_sink": (n.code == "NODE-08" and mesh_manager.cellular_blackout),
            "parent_code": n.parent.code if n.parent else None
        })

    link_list = []
    for l in links:
        source_node = node_dict.get(l.from_node_id)
        target_node = node_dict.get(l.to_node_id)
        if source_node and target_node:
            link_list.append({
                "id": l.id,
                "source": source_node.code,
                "target": target_node.code,
                "rssi": l.rssi,
                "link_type": l.link_type,
                "active": l.active
            })

    mode_str = "DECENTRALIZED_LORA_MESH" if mesh_manager.cellular_blackout else "HYBRID_CELLULAR"

    return {
        "network_mode": mode_str,
        "cellular_blackout": mesh_manager.cellular_blackout,
        "active_gateways": active_gateways,
        "total_mesh_hops": total_hops,
        "backup_sink_active": mesh_manager.cellular_blackout,
        "backup_sink_node": "NODE-08",
        "nodes": node_list,
        "links": link_list
    }

@router.post("/blackout", response_model=dict)
async def toggle_mesh_blackout(enabled: bool, db: Session = Depends(get_db)):
    """
    Simulates cellular blackout.
    When enabled, primary cellular gateway drops and packets dynamically reroute to NODE-08 (LoRa Satellite Backup Sink).
    """
    mesh_manager.cellular_blackout = enabled
    nodes = db.query(Node).all()

    for n in nodes:
        if enabled:
            if n.code == "GW-01":
                n.status = "offline"
            elif n.code == "NODE-08":
                n.is_gateway = True
                n.status = "normal"
            else:
                if n.parent and n.parent.code == "GW-01":
                    node8 = db.query(Node).filter(Node.code == "NODE-08").first()
                    if node8:
                        n.parent_node_id = node8.id
        else:
            if n.code == "GW-01":
                n.is_gateway = True
                n.status = "normal"
            elif n.code == "NODE-08":
                n.is_gateway = False
            else:
                gw = db.query(Node).filter(Node.code == "GW-01").first()
                if gw and n.mesh_level == 1:
                    n.parent_node_id = gw.id

    db.commit()

    mode_str = "DECENTRALIZED_LORA_MESH" if enabled else "HYBRID_CELLULAR"

    await ws_manager.broadcast("mesh_change", {
        "cellular_blackout": enabled,
        "network_mode": mode_str,
        "backup_sink": "NODE-08" if enabled else None
    })

    return {
        "cellular_blackout": enabled,
        "network_mode": mode_str,
        "message": (
            "⚠️ Cellular blackout active! Dynamic failover: Packets rerouted to NODE-08 (Emergency LoRa Satellite Sink)."
            if enabled else "Cellular infrastructure restored. Hybrid gateway active."
        )
    }
