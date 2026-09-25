from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class MeshLink(Base):
    __tablename__ = "mesh_links"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    from_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    to_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    rssi = Column(Float, default=-65.0)
    link_type = Column(String(20), default="esp_now")  # esp_now, lora, cellular
    active = Column(Boolean, default=True)

    from_node = relationship("Node", foreign_keys=[from_node_id])
    to_node = relationship("Node", foreign_keys=[to_node_id])
