@echo off
title Intelligent Waste Collection System Launcher

echo ========================================================
echo   Launching Intelligent Waste Collection System...
echo ========================================================
echo.

:: 1. Start Python FastAPI Backend in a new window
echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000...
start "FastAPI Backend Server" cmd /k "cd /d "%~dp0" && python backend\main.py"

:: Timeout 3 seconds for backend initialization
timeout /t 3 /nobreak >nul

:: 2. Start React Vite Frontend in a new window
echo [2/2] Starting React Vite Frontend...
start "React Frontend Server" cmd /k "cd /d "%~dp0frontend" && npm install && npm run dev"

echo.
echo ========================================================
echo   Both servers are starting in separate windows!
echo   - Backend: http://127.0.0.1:8000
echo   - Frontend: http://localhost:3000
echo ========================================================
echo.
pause
