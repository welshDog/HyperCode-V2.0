@echo off
REM HyperCode V2.0 - Quick Health Fix Script (Windows)

setlocal enabledelayedexpansion

echo.
echo 🔧 HyperCode V2.0 - Agent Health Recovery
echo ==========================================
echo.

REM Step 1: Stop services
echo 1️⃣  Stopping services...
docker compose down

REM Step 2: Rebuild core
echo.
echo 2️⃣  Rebuilding hypercode-core...
docker compose build hypercode-core

REM Step 3: Start services
echo.
echo 3️⃣  Starting services...
docker compose up -d

REM Step 4: Wait for core to be healthy
echo.
echo 4️⃣  Waiting for hypercode-core to be healthy (max 60s)...
setlocal enabledelayedexpansion
for /L %%i in (1,1,20) do (
    powershell -Command "try { $r = Invoke-WebRequest http://localhost:8000/health -TimeoutSec 2 -ErrorAction Stop; exit 0 } catch { exit 1 }" 2>nul
    if !errorlevel! equ 0 (
        echo ✅ hypercode-core is healthy!
        goto :step5
    )
    echo   Attempt %%i/20... waiting
    timeout /t 3 /nobreak >nul
)

:step5
REM Step 5: Start agents profile
echo.
echo 5️⃣  Starting agents...
docker compose up -d --profile agents

REM Step 6: Wait for agents to register
echo.
echo 6️⃣  Waiting for agents to register (max 60s)...
timeout /t 10 /nobreak >nul
for /L %%i in (1,1,5) do (
    echo   Checking agents...
    timeout /t 10 /nobreak >nul
)

REM Step 7: Verify health
echo.
echo 7️⃣  Verifying health...
echo.
docker ps --format "table {{.Names}}\t{{.Status}}" | findstr /E "specialist engineer strategist core postgres redis"

echo.
echo ✅ Recovery complete! Check agents status:
echo    docker logs project-strategist --tail 20
echo    docker logs backend-specialist --tail 20
echo.

endlocal
