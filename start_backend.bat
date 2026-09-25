@echo off
title TERRA SHIELD - Backend & AI Engine
cd /d "%~dp0backend"
echo =================================================================
echo  TERRA SHIELD - AI-Powered Environmental Monitoring Network
echo  Starting FastAPI Backend & WebSocket Engine on http://localhost:8000
echo =================================================================
call venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
