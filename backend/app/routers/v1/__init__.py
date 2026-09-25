from fastapi import APIRouter

from app.routers.v1.auth import router as auth_router
from app.routers.v1.ingest import router as ingest_router
from app.routers.v1.nodes import router as nodes_router
from app.routers.v1.alerts import router as alerts_router
from app.routers.v1.mesh import router as mesh_router
from app.routers.v1.zones import router as zones_router
from app.routers.v1.contacts import router as contacts_router
from app.routers.v1.weather import router as weather_router
from app.routers.v1.news import router as news_router
from app.routers.v1.stats import router as stats_router
from app.routers.v1.citizen import router as citizen_router
from app.routers.v1.demo import router as demo_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(ingest_router)
v1_router.include_router(nodes_router)
v1_router.include_router(alerts_router)
v1_router.include_router(mesh_router)
v1_router.include_router(zones_router)
v1_router.include_router(contacts_router)
v1_router.include_router(weather_router)
v1_router.include_router(news_router)
v1_router.include_router(stats_router)
v1_router.include_router(citizen_router)
v1_router.include_router(demo_router)

__all__ = ["v1_router"]
