"""
TERRA SHIELD - Multi-Node IoT Mesh Network Telemetry Simulator v2.0
Simulates 20 autonomous edge sensor nodes streaming telemetry packets to the backend.
Supports SHA-256 API Key authentication, physical nodes (PHY-01..PHY-05),
store-and-forward flash buffering on comms outage, and CLI triggers.
"""

import sys
import time
import random
import math
import argparse
import requests
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [SIMULATOR] %(message)s")
logger = logging.getLogger("IoT_Mesh_Simulator")

DEFAULT_SERVER_URL = "http://127.0.0.1:8000"
SIMULATOR_API_KEY = "ts_sim_master_key_2026"

PHYSICAL_KEYS = {
    "PHY-01": "ts_live_phy-01_64f88c22889172f1b5b5fba7",
    "PHY-02": "ts_live_phy-02_2c740691a988030224cac7bd",
    "PHY-03": "ts_live_phy-03_60a6f1622ed3586ee0e8d612",
    "PHY-04": "ts_live_phy-04_d446affeb8efdefb2482c5cc",
    "PHY-05": "ts_live_phy-05_8c3727d15f4cf097a7ee1067",
}

# 20 Nodes: 5 Hardware + 15 Mesh Relays
NODES = [
    # Physical Hardware nodes
    {"id": "PHY-01", "type": "HARDWARE", "hops": 0, "parent": None, "water_base": 1.6, "temp_base": 28.0, "pm25_base": 35.0},
    {"id": "PHY-02", "type": "HARDWARE", "hops": 1, "parent": "PHY-01", "water_base": 1.7, "temp_base": 27.5, "pm25_base": 38.0},
    {"id": "PHY-03", "type": "HARDWARE", "hops": 1, "parent": "PHY-01", "water_base": 4.85, "temp_base": 27.5, "pm25_base": 30.0},
    {"id": "PHY-04", "type": "HARDWARE", "hops": 2, "parent": "PHY-02", "water_base": 2.2, "temp_base": 26.8, "pm25_base": 32.0},
    {"id": "PHY-05", "type": "HARDWARE", "hops": 2, "parent": "PHY-03", "water_base": 3.4, "temp_base": 27.0, "pm25_base": 36.0},

    # Simulated Mesh Nodes
    {"id": "GW-01", "type": "SIMULATED", "hops": 0, "parent": None, "water_base": 2.0, "temp_base": 27.0, "pm25_base": 45.0},
    {"id": "NODE-01", "type": "SIMULATED", "hops": 1, "parent": "GW-01", "water_base": 3.5, "temp_base": 26.5, "pm25_base": 42.0},
    {"id": "NODE-02", "type": "SIMULATED", "hops": 2, "parent": "NODE-01", "water_base": 3.6, "temp_base": 25.8, "pm25_base": 38.0},
    {"id": "NODE-03", "type": "SIMULATED", "hops": 3, "parent": "NODE-02", "water_base": 4.65, "temp_base": 25.0, "pm25_base": 35.0},
    {"id": "NODE-04", "type": "SIMULATED", "hops": 4, "parent": "NODE-03", "water_base": 4.25, "temp_base": 24.5, "pm25_base": 30.0},
    {"id": "NODE-05", "type": "SIMULATED", "hops": 5, "parent": "NODE-04", "water_base": 1.9, "temp_base": 24.0, "pm25_base": 28.0},
    {"id": "NODE-06", "type": "SIMULATED", "hops": 1, "parent": "GW-01", "water_base": 0.4, "temp_base": 32.0, "pm25_base": 55.0},
    {"id": "NODE-07", "type": "SIMULATED", "hops": 2, "parent": "NODE-06", "water_base": 0.3, "temp_base": 34.5, "pm25_base": 60.0},
    {"id": "NODE-08", "type": "SIMULATED", "hops": 2, "parent": "NODE-03", "water_base": 0.5, "temp_base": 31.0, "pm25_base": 48.0},
    {"id": "NODE-09", "type": "SIMULATED", "hops": 1, "parent": "GW-01", "water_base": 0.4, "temp_base": 30.5, "pm25_base": 50.0},
    {"id": "NODE-10", "type": "SIMULATED", "hops": 2, "parent": "NODE-09", "water_base": 0.3, "temp_base": 33.0, "pm25_base": 58.0},
    {"id": "NODE-11", "type": "SIMULATED", "hops": 1, "parent": "GW-01", "water_base": 1.5, "temp_base": 28.0, "pm25_base": 85.0},
    {"id": "NODE-12", "type": "SIMULATED", "hops": 1, "parent": "GW-01", "water_base": 1.4, "temp_base": 28.5, "pm25_base": 78.0},
    {"id": "NODE-13", "type": "SIMULATED", "hops": 2, "parent": "NODE-12", "water_base": 1.5, "temp_base": 29.0, "pm25_base": 115.0},
    {"id": "NODE-14", "type": "SIMULATED", "hops": 2, "parent": "NODE-01", "water_base": 1.7, "temp_base": 27.5, "pm25_base": 65.0},
]

# Simulated local LittleFS store-and-forward buffers for severed nodes
offline_buffers = {}
severed_nodes = set()

def get_node_key(node_id: str) -> str:
    return PHYSICAL_KEYS.get(node_id, SIMULATOR_API_KEY)

def send_reading(server_url: str, payload: dict) -> bool:
    node_id = payload["node_id"]
    endpoint = f"{server_url}/api/v1/ingest/reading"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": get_node_key(node_id)
    }

    if node_id in severed_nodes:
        # Buffer locally (simulating LittleFS)
        if node_id not in offline_buffers:
            offline_buffers[node_id] = []
        offline_buffers[node_id].append(payload)
        logger.info(f"[STORE-FORWARD] Node {node_id} is severed. Buffered reading (total {len(offline_buffers[node_id])} in queue)")
        return True

    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=3.0)
        if resp.status_code in (200, 201):
            data = resp.json()
            if data.get("alert_triggered"):
                logger.warning(f"🚨 ALERT TRIGGERED on {node_id}: {data}")
            return True
        else:
            logger.error(f"Failed to ingest for {node_id}: HTTP {resp.status_code} - {resp.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"Ingest connection error for {node_id}: {e}")
        return False

def flush_store_forward_buffer(server_url: str, node_id: str):
    if node_id not in offline_buffers or not offline_buffers[node_id]:
        logger.info(f"No buffered readings to flush for {node_id}.")
        return

    records = offline_buffers[node_id]
    logger.info(f"📶 Comms restored on {node_id}! Flushing {len(records)} buffered records to /api/v1/ingest/store-forward...")

    endpoint = f"{server_url}/api/v1/ingest/store-forward"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": get_node_key(node_id)
    }

    try:
        resp = requests.post(endpoint, json=records, headers=headers, timeout=5.0)
        if resp.status_code in (200, 201):
            logger.info(f"✅ Flush successful! {resp.json()}")
            offline_buffers[node_id] = []
            severed_nodes.discard(node_id)
        else:
            logger.error(f"Flush failed: HTTP {resp.status_code} - {resp.text}")
    except Exception as e:
        logger.error(f"Error flushing store-and-forward batch: {e}")

def trigger_hazard(server_url: str, node_id: str, hazard_type: str):
    logger.info(f"Injecting hazard {hazard_type} on {node_id}...")
    endpoint = f"{server_url}/api/v1/demo/trigger"
    try:
        resp = requests.post(endpoint, json={"node_id": node_id, "type": hazard_type}, timeout=3.0)
        logger.info(f"Hazard trigger result: {resp.status_code} - {resp.json()}")
    except Exception as e:
        logger.error(f"Failed to trigger hazard: {e}")

def run_simulator(server_url: str = DEFAULT_SERVER_URL, interval_seconds: float = 3.0, iterations: int = 0):
    logger.info(f"Starting IoT Mesh Telemetry Stream (20 nodes) to {server_url}...")
    tick = 0
    batteries = {n["id"]: random.uniform(92.0, 99.0) for n in NODES}

    while True:
        tick += 1
        selected_nodes = random.sample(NODES, k=min(5, len(NODES)))

        for node in selected_nodes:
            noise_water = math.sin(tick * 0.1) * 0.12 + random.uniform(-0.03, 0.03)
            noise_temp = math.cos(tick * 0.05) * 1.2 + random.uniform(-0.2, 0.2)
            noise_hum = random.uniform(-2.0, 2.0)
            noise_pm = random.uniform(-4.0, 4.0)

            water_m = round(max(0.2, node["water_base"] + noise_water), 2)
            temp_c = round(node["temp_base"] + noise_temp, 1)
            hum_pct = round(max(10.0, min(95.0, 60.0 - (temp_c - 25.0) * 1.8 + noise_hum)), 1)
            wind_spd = round(random.uniform(6.0, 18.0), 1)
            wind_dir = round(random.uniform(0.0, 360.0), 1)
            pm25 = round(max(5.0, node["pm25_base"] + noise_pm), 1)
            pm10 = round(pm25 * random.uniform(1.4, 1.8), 1)

            batteries[node["id"]] = max(10.0, batteries[node["id"]] - 0.003)
            battery_pct = round(batteries[node["id"]], 1)

            payload = {
                "node_id": node["id"],
                "water_level_m": water_m,
                "temperature_c": temp_c,
                "humidity_pct": hum_pct,
                "wind_speed_kmh": wind_spd,
                "wind_direction_deg": wind_dir,
                "pm25": pm25,
                "pm10": pm10,
                "mesh_hops": node["hops"],
                "parent_node_id": node["parent"],
                "battery_pct": battery_pct,
                "signal_rssi": round(-52.0 - (node["hops"] * 8.5) + random.uniform(-1.5, 1.5), 1),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            send_reading(server_url, payload)

        if iterations > 0 and tick >= iterations:
            logger.info(f"Completed {iterations} iterations.")
            break

        time.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TERRA SHIELD IoT Mesh Telemetry Simulator")
    parser.add_argument("--url", default=DEFAULT_SERVER_URL, help="Backend API base URL")
    parser.add_argument("--interval", type=float, default=3.0, help="Loop interval in seconds")
    parser.add_argument("--iterations", type=int, default=0, help="Number of ticks (0 for continuous)")
    parser.add_argument("--trigger", choices=["flood", "wildfire", "smoke", "normal"], help="Inject hazard condition")
    parser.add_argument("--node", default="PHY-01", help="Target node for trigger or network control")
    parser.add_argument("--cut-network", metavar="NODE_ID", help="Sever network on node (begins LittleFS buffering)")
    parser.add_argument("--restore-network", metavar="NODE_ID", help="Restore network on node (flushes LittleFS buffer)")

    args = parser.parse_args()

    if args.trigger:
        trigger_hazard(args.url, args.node, args.trigger)
    elif args.cut_network:
        severed_nodes.add(args.cut_network)
        logger.info(f"Node {args.cut_network} comms cut. Run simulator to accumulate buffer.")
    elif args.restore_network:
        flush_store_forward_buffer(args.url, args.restore_network)
    else:
        run_simulator(server_url=args.url, interval_seconds=args.interval, iterations=args.iterations)
