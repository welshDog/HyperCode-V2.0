# BROski Pantheon 2.0 - Comprehensive Test Executor
# Runs Unit, Integration, and System tests

$ErrorActionPreference = "Continue"
$Root = Get-Location
$ReportDir = "$Root\test_reports"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null

Write-Host "STARTING COMPREHENSIVE TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================"

# 1. Backend Tests (Python/Pytest)
Write-Host "`n1. Running Backend Unit and Integration Tests..." -ForegroundColor Yellow
Set-Location "$Root\THE HYPERCODE\hypercode-core"
try {
    # Ensure dependencies are installed (assuming python is available)
    # python -m pip install -r requirements.txt | Out-Null
    
    # Run pytest
    pytest > "$ReportDir\backend_results.txt" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PASS: Backend Tests Passed" -ForegroundColor Green
    } else {
        Write-Host "FAIL: Backend Tests Failed" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Running backend tests: $_" -ForegroundColor Red
}

# 2. Frontend Tests (Node/Vitest)
Write-Host "`n2. Running Frontend Unit Tests..." -ForegroundColor Yellow
Set-Location "$Root\BROski Business Agents\broski-terminal"
try {
    # Check if node_modules exists, install if not
    if (-not (Test-Path "node_modules")) {
        Write-Host "   Installing frontend dependencies..."
        npm install | Out-Null
    }
    
    # Run Vitest (Unit)
    npm test -- --run > "$ReportDir\frontend_unit_results.txt" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PASS: Frontend Unit Tests Passed" -ForegroundColor Green
    } else {
        Write-Host "FAIL: Frontend Unit Tests Failed" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Running frontend tests: $_" -ForegroundColor Red
}

# 3. System/Scenario Tests
Write-Host "`n3. Running System Scenario Tests..." -ForegroundColor Yellow
Set-Location "$Root"
try {
    # Run the python test runner
    $env:PYTHONPATH = "$Root"
    python tests/run_tests.py --url http://localhost:8000 > "$ReportDir\system_scenario_results.txt" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PASS: System Tests Passed" -ForegroundColor Green
    } else {
        Write-Host "FAIL: System Tests Failed" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Running system tests: $_" -ForegroundColor Red
}

# 4. Agent Connectivity Check (Docker)
Write-Host "`n4. Checking Agent Docker Containers..." -ForegroundColor Yellow
try {
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" > "$ReportDir\docker_status.txt"
    Write-Host "PASS: Docker Status Captured" -ForegroundColor Green
} catch {
    Write-Host "FAIL: Failed to check Docker status" -ForegroundColor Red
}

Set-Location $Root
Write-Host "`n========================================"
Write-Host "Testing Complete. Reports generated in $ReportDir" -ForegroundColor Cyan
exit 0
