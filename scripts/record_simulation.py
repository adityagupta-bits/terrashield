import os
import time
import subprocess
import requests
from PIL import Image

ARTIFACT_DIR = r"C:\Users\ASUS\.gemini\antigravity-ide\brain\046ef912-d97b-4ad0-ad52-d542c202016c"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_FRAMES_DIR = os.path.join(ARTIFACT_DIR, "simulation_frames")
os.makedirs(OUTPUT_FRAMES_DIR, exist_ok=True)

BACKEND_URL = "http://127.0.0.1:8000/api"
FRONTEND_URL = "http://localhost:5173"

def capture_screen(url, filename, delay_budget=3500):
    dest_path = os.path.join(OUTPUT_FRAMES_DIR, filename)
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--window-size=1600,950",
        f"--virtual-time-budget={delay_budget}",
        f"--screenshot={dest_path}",
        url
    ]
    subprocess.run(cmd, check=True)
    print(f"Captured: {filename} -> {dest_path}")
    return dest_path

def main():
    print("=== Step 1: Baseline Command Center ===")
    try:
        requests.post(f"{BACKEND_URL}/simulation/trigger?scenario=RESET", timeout=5)
    except Exception as e:
        print(f"Reset trigger notice: {e}")
    time.sleep(1)
    frame1 = capture_screen(f"{FRONTEND_URL}/", "01_command_center_baseline.png", 3500)

    print("=== Step 2: Trigger Flash Flood Surge ===")
    try:
        requests.post(f"{BACKEND_URL}/simulation/trigger?scenario=FLASH_FLOOD", timeout=5)
    except Exception as e:
        print(f"Flood trigger notice: {e}")
    time.sleep(1)
    frame2 = capture_screen(f"{FRONTEND_URL}/", "02_flash_flood_surge.png", 3500)

    print("=== Step 3: Trigger Wildfire Scenario ===")
    try:
        requests.post(f"{BACKEND_URL}/simulation/trigger?scenario=WILDFIRE", timeout=5)
    except Exception as e:
        print(f"Wildfire trigger notice: {e}")
    time.sleep(1)
    frame3 = capture_screen(f"{FRONTEND_URL}/", "03_wildfire_hotspot.png", 3500)

    print("=== Step 4: Citizen Safety Portal (Hindi) ===")
    frame4 = capture_screen(f"{FRONTEND_URL}?view=user", "04_citizen_portal_hi.png", 3500)

    print("=== Step 5: Reset Baseline ===")
    try:
        requests.post(f"{BACKEND_URL}/simulation/trigger?scenario=RESET", timeout=5)
    except Exception as e:
        pass
    time.sleep(1)
    frame5 = capture_screen(f"{FRONTEND_URL}/", "05_system_optimal_reset.png", 3500)

    frames = [frame1, frame2, frame3, frame4, frame5]
    images = [Image.open(f).convert("RGB") for f in frames if os.path.exists(f)]

    if images:
        # Save as animated WebP
        webp_path = os.path.join(ARTIFACT_DIR, "simulation_walkthrough.webp")
        images[0].save(
            webp_path,
            save_all=True,
            append_images=images[1:],
            duration=[3200, 3800, 3800, 4200, 3200],
            loop=0,
            quality=88
        )
        print(f"Successfully generated animated WebP: {webp_path}")

        # Also save as animated GIF for universal playback
        gif_path = os.path.join(ARTIFACT_DIR, "simulation_walkthrough.gif")
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=[3200, 3800, 3800, 4200, 3200],
            loop=0
        )
        print(f"Successfully generated animated GIF: {gif_path}")

if __name__ == "__main__":
    main()
