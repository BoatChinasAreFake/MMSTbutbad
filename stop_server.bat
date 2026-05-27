@echo off
title Stop Map Sandbox Server
cd /d "%~dp0"

echo Stopping Map Sandbox Server on port 8000...

:: Find and kill process on port 8000
set "found="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
    set "found=1"
)

if defined found (
    echo Server stopped successfully.
) else (
    echo No running server found on port 8000.
)

timeout /t 2 >nul
exit
