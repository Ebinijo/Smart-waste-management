@echo off
title React Frontend Server
cd /d "%~dp0frontend"
echo Installing frontend dependencies if needed...
call npm install
echo Starting React Vite Frontend Server...
call npm run dev
pause
