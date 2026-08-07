@echo off
title Mappa Mundi - Province Sync & Centroid Recomputation
echo =======================================================================
echo               MAPPA MUNDI - PROVINCE SYNCHRONIZATION TOOL
echo =======================================================================
echo.

echo [Step 1/2] Running Smart Province Sync & Parent Data Inheritance...
python C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\scratch\smart_sync_provinces.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Synchronization script failed!
    echo.
    pause
    exit /b %ERRORLEVEL%
)
echo.

echo [Step 2/2] Recalculating All Province Centroids and Sizes...
python C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\scratch\recompute_all_province_centers.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Centroid recomputation failed!
    echo.
    pause
    exit /b %ERRORLEVEL%
)
echo.

echo =======================================================================
echo SUCCESS: All provinces synchronized, cored, and hitboxes calibrated!
echo Please reload your browser page to see the changes.
echo =======================================================================
echo.
pause
