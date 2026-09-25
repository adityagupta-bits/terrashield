import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import engine, Base, SessionLocal
from app.models.nodes import Node
from app.mesh_manager import mesh_manager
from app.websocket_manager import ws_manager

# Import v1 routers and webhook
from app.routers.v1 import v1_router
from app.routers.whatsapp_webhook import router as whatsapp_webhook_router

# Import existing legacy routers for full backward compatibility
from app.routers import telemetry, nodes, alerts, whatsapp, simulation
from app.routers.nodes import seed_default_nodes_and_shelters

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TERRA_SHIELD")

async def background_offline_node_checker():
    """
    Periodic background monitor:
    Checks for nodes where last_seen > 120 seconds.
    Marks them 'offline' and broadcasts 'node_status' event over WebSocket.
    """
    while True:
        try:
            await asyncio.sleep(15)
            db = SessionLocal()
            try:
                threshold_time = datetime.utcnow() - timedelta(seconds=120)
                stale_nodes = (
                    db.query(Node)
                    .filter(Node.last_seen < threshold_time, Node.status != "offline")
                    .all()
                )
                for node in stale_nodes:
                    node.status = "offline"
                    db.commit()
                    logger.info(f"Node {node.code} marked OFFLINE (last seen > 120s)")
                    await ws_manager.broadcast("node_status", {
                        "node_id": node.id,
                        "node_code": node.code,
                        "status": "offline",
                        "battery_pct": node.battery_pct,
                        "signal_strength": node.signal_strength
                    })
            finally:
                db.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"Error in offline node checker: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist
    logger.info("Initializing TERRA SHIELD Spatial & Disaster Database...")
    Base.metadata.create_all(bind=engine)

    # Check if database needs seeding
    db = SessionLocal()
    try:
        if db.query(Node).count() == 0:
            logger.info("Empty database detected. Running automated initial seed...")
            from scripts.seed import seed_database
            seed_database()
    except Exception as e:
        logger.warning(f"Seed verification notice: {e}")
    finally:
        db.close()

    # Start background node heartbeat monitor
    offline_task = asyncio.create_task(background_offline_node_checker())

    yield

    # Shutdown
    offline_task.cancel()
    logger.info("TERRA SHIELD Backend shutting down.")

app = FastAPI(
    title=f"{settings.PROJECT_NAME} Disaster Monitoring Engine",
    description="Resilient AI-Powered Multi-Hazard Environmental Monitoring Network with Offline Mesh & Vernacular WhatsApp Verification (SIH26178)",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Versioned API v1 Router
app.include_router(v1_router)

# Mount WhatsApp Webhook
app.include_router(whatsapp_webhook_router)

# Mount Legacy Routers for 100% Backward Compatibility
app.include_router(telemetry.router, prefix=settings.API_PREFIX)
app.include_router(nodes.router, prefix=settings.API_PREFIX)
app.include_router(alerts.router, prefix=settings.API_PREFIX)
app.include_router(whatsapp.router, prefix=settings.API_PREFIX)
app.include_router(simulation.router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "problem_statement": settings.PROJECT_ID,
        "status": "OPERATIONAL",
        "version": "2.0.0",
        "docs_url": "/docs",
        "v1_api_base": "/api/v1",
        "websocket_endpoint": "/ws/live"
    }

@app.websocket("/ws/live")
async def websocket_live_stream(websocket: WebSocket):
    """Real-time bi-directional WebSocket connection for Authorities Command & Control Dashboard."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Echo heartbeat / receive pings
            data = await websocket.receive_text()
            await websocket.send_text('{"type": "pong"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        ws_manager.disconnect(websocket)
