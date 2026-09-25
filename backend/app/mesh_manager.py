import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import SensorNode
from app.schemas import MeshTopologyResponse, MeshTopologyLink, SensorNodeResponse

logger = logging.getLogger(__name__)

class MeshNetworkManager:
    def __init__(self):
        self.cellular_blackout: bool = False

    def toggle_cellular_blackout(self, db: Session, blackout: bool) -> bool:
        """
        Toggles between normal hybrid cellular mode and complete cellular blackout mode.
        When blackout is active, cellular gateway drops and network shifts to 100% decentralized mesh.
        """
        self.cellular_blackout = blackout
        nodes = db.query(SensorNode).all()
        
        for node in nodes:
            if blackout:
                # Gateway loses direct cellular uplink; must rely on local mesh buffer or long-range LoRa sink
                if node.id == "GW-01":
                    node.status = "OFFLINE_CELLULAR"
                    node.hop_count = 99
                elif node.id == "NODE-08":  # Node 8 becomes emergency LoRa Satellite sink
                    node.is_gateway = True
                    node.status = "EMERGENCY_SINK"
                    node.hop_count = 0
                    node.parent_node_id = None
                else:
                    node.status = "MESH_RELAY"
                    if node.parent_node_id == "GW-01":
                        node.parent_node_id = "NODE-08"
            else:
                # Reset to normal hybrid mode
                if node.id == "GW-01":
                    node.is_gateway = True
                    node.status = "GATEWAY"
                    node.hop_count = 0
                    node.parent_node_id = None
                elif node.id == "NODE-08":
                    node.is_gateway = False
                    node.status = "ONLINE"
                else:
                    node.status = "ONLINE" if node.hop_count == 1 else "MESH_RELAY"

        db.commit()
        logger.info(f"Cellular blackout status changed to: {blackout}")
        return self.cellular_blackout

    def get_topology(self, db: Session) -> MeshTopologyResponse:
        nodes = db.query(SensorNode).all()
        links: List[MeshTopologyLink] = []
        active_gateways = 0
        total_hops = 0

        node_dict = {n.id: n for n in nodes}

        for n in nodes:
            if n.is_gateway and n.status != "OFFLINE_CELLULAR":
                active_gateways += 1
            
            total_hops += n.hop_count

            if n.parent_node_id and n.parent_node_id in node_dict:
                links.append(
                    MeshTopologyLink(
                        source=n.id,
                        target=n.parent_node_id,
                        hop_level=n.hop_count,
                        signal_rssi=n.signal_rssi
                    )
                )

        mode_str = "DECENTRALIZED_MESH_BLACKOUT" if self.cellular_blackout else "HYBRID_CELLULAR"

        return MeshTopologyResponse(
            network_mode=mode_str,
            nodes=[SensorNodeResponse.model_validate(n) for n in nodes],
            links=links,
            active_gateways=active_gateways,
            total_mesh_hops=total_hops
        )

mesh_manager = MeshNetworkManager()
