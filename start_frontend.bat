@echo off
title TERRA SHIELD - Mission Control Dashboard
cd /d "%~dp0frontend"
echo =================================================================
echo  TERRA SHIELD - Mission Control & GIS Dashboard
echo  Starting Vite Dev Server on http://localhost:5173
echo =================================================================
npm run dev
pause
