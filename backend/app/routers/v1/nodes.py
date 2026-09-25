from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.nodes import Node
from app.models.readings import Reading
from app.schemas.v1_schemas import NodeResponse

router = APIRouter(prefix="/nodes", tags=["Nodes"])

@router.get("", response_model=List[NodeResponse])
def get_all_nodes(db: Session = Depends(get_db)):
    """Returns all physical and simulated nodes with their status and telemetry."""
    nodes = db.query(Node).all()
    results = []
    for n in nodes:
        parent_code = n.parent.code if n.parent else None
        results.append(
            NodeResponse(
                id=n.id,
                code=n.code,
                name=n.name,
                hazard_type=n.hazard_type,
                latitude=n.latitude,
                longitude=n.longitude,
                status=n.status,
                battery_pct=n.battery_pct,
                signal_strength=n.signal_strength,
                mesh_level=n.mesh_level,
                parent_node_id=n.parent_node_id,
                parent_code=parent_code,
                is_gateway=n.is_gateway,
                is_simulated=n.is_simulated,
                last_seen=n.last_seen
            )
        )
    return results

@router.get("/{id}", response_model=NodeResponse)
def get_node_by_id(id: str, db: Session = Depends(get_db)):
    """Fetches a single node by integer ID or string code (e.g. 1 or 'PHY-01')."""
    if id.isdigit():
        node = db.query(Node).filter(Node.id == int(id)).first()
    else:
        node = db.query(Node).filter(Node.code == id).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    parent_code = node.parent.code if node.parent else None
    return NodeResponse(
        id=node.id,
        code=node.code,
        name=node.name,
        hazard_type=node.hazard_type,
        latitude=node.latitude,
        longitude=node.longitude,
        status=node.status,
        battery_pct=node.battery_pct,
        signal_strength=node.signal_strength,
        mesh_level=node.mesh_level,
        parent_node_id=node.parent_node_id,
        parent_code=parent_code,
        is_gateway=node.is_gateway,
        is_simulated=node.is_simulated,
        last_seen=node.last_seen
    )

@router.get("/{id}/readings", response_model=List[dict])
def get_node_readings(id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Returns the last N historical readings for a node for live sparkline charting."""
    if id.isdigit():
        node = db.query(Node).filter(Node.id == int(id)).first()
    else:
        node = db.query(Node).filter(Node.code == id).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    readings = (
        db.query(Reading)
        .filter(Reading.node_id == node.id)
        .order_by(desc(Reading.ts))
        .limit(limit)
        .all()
    )

    results = []
    for r in reversed(readings):
        results.append({
            "id": r.id,
            "ts": r.ts.isoformat(),
            "water_level_cm": r.water_level_cm,
            "water_rate_cm_min": r.water_rate_cm_min,
            "pm25": r.pm25,
            "pm10": r.pm10,
            "temperature_c": r.temperature_c,
            "humidity": r.humidity,
            "smoke_index": r.smoke_index,
            "raw_bytes": r.raw_bytes,
            "tx_bytes": r.tx_bytes
        })
    return results
