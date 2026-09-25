@echo off
title TERRA SHIELD - Launch All Systems
echo =================================================================
echo  TERRA SHIELD (SIH26178) - Launching Complete Ecosystem
echo =================================================================
echo 1. Launching Backend & AI Engine on http://localhost:8000 ...
start "TERRA SHIELD - Backend" cmd /c "start_backend.bat"

timeout /t 3 /nobreak > nul

echo 2. Launching Mission Control Dashboard on http://localhost:5173 ...
start "TERRA SHIELD - Dashboard" cmd /c "start_frontend.bat"

timeout /t 3 /nobreak > nul

echo 3. Launching 15-Node Autonomous Mesh Telemetry Simulator ...
start "TERRA SHIELD - Simulator" cmd /c "start_simulator.bat"

echo.
echo All subsystems launched!
echo Open your browser to: http://localhost:5173
pause
