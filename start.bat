@echo off
REM Quick start script for HyperCode
REM Usage: start.bat [dev|prod|agents]

setlocal enabledelayedexpansion

set MODE=%1
if "%MODE%"=="" set MODE=dev

if not exist .env (
    echo Error: .env file not found
    echo Please copy .env.example to .env and configure it
    exit /b 1
)

echo ========================================
echo  HyperCode Startup Script
echo ========================================
echo.
echo Mode: %MODE%
echo.

if "%MODE%"=="dev" (
    echo Starting development environment...
    set ENVIRONMENT=development
    docker-compose -f docker-compose.yml up -d
    timeout /t 5 /nobreak
    docker-compose -f docker-compose.yml ps
    echo.
    echo Dashboard: http://localhost:8088
    echo Terminal: http://localhost:3000
    echo Grafana: http://localhost:3001
)

if "%MODE%"=="prod" (
    echo Starting production environment...
    set ENVIRONMENT=production
    docker-compose -f docker-compose.yml up -d
    timeout /t 5 /nobreak
    docker-compose -f docker-compose.yml ps
)

if "%MODE%"=="agents" (
    echo Starting with agents...
    set ENVIRONMENT=development
    docker-compose -f docker-compose.yml --profile agents up -d
    timeout /t 5 /nobreak
    docker-compose -f docker-compose.yml --profile agents ps
)

echo.
echo Done! Run 'docker-compose -f docker-compose.yml ps' to see status
echo Run 'python scripts/health-monitor.py' to check service health
