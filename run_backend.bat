@echo off
title FastAPI Backend Server
cd /d "%~dp0"
echo Starting FastAPI Backend on http://127.0.0.1:8000...
python backend\main.py
pause
