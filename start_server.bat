@echo off
title Map Sandbox Server
cd /d "%~dp0"

:: Check if port 8000 is in use, and kill the process holding it
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: Start python server invisibly using PowerShell
start "" powershell -WindowStyle Hidden -Command "python -m http.server 8000"

:: Wait 1 second to make sure the server is up before the browser opens
ping 127.0.0.1 -n 2 >nul

:: Open the browser
start "" http://localhost:8000

exit