@echo off
title TERRA SHIELD - 20-Node IoT Mesh Simulator
cd /d "%~dp0"
echo =================================================================
echo  TERRA SHIELD - 20-Node Autonomous Mesh Telemetry Simulator (5 Hardware)
echo  Streaming physics-based packets to http://localhost:8000
echo =================================================================
backend\venv\Scripts\python.exe simulator\iot_mesh_simulator.py
pause
