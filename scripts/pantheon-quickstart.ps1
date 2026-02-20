# BROski Pantheon 2.0 - Quick Start Validation (Windows)
# Checks your environment for the new agent framework

Write-Host "� BROski Pantheon 2.0 - System Check" -ForegroundColor Cyan
Write-Host "========================================"

$ErrorActionPreference = "Stop"

function Test-Command ($command) {
    if (Get-Command $command -ErrorAction SilentlyContinue) {
        Write-Host "✅ Found $command" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Missing $command" -ForegroundColor Red
        return $false
    }
}

function Test-File ($path) {
    if (Test-Path $path) {
        Write-Host "✅ Found $path" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ Missing $path" -ForegroundColor Red
        return $false
    }
}

# 1. Check Docker
Write-Host "`n1. Checking Docker Environment..." -ForegroundColor Yellow
if (Test-Command "docker") {
    $dockerVersion = docker --version
    Write-Host "   $dockerVersion" -ForegroundColor Gray
    
    try {
        docker info > $null 2>&1
        Write-Host "✅ Docker Daemon is running" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker Daemon is NOT running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Docker not installed. Install Docker Desktop 4.49+" -ForegroundColor Red
    exit 1
}

# 2. Check Files
Write-Host "`n2. Checking Pantheon Files..." -ForegroundColor Yellow
$missingFiles = 0
if (-not (Test-File ".\cagent-pantheon.yaml")) { $missingFiles++ }
if (-not (Test-File ".\agents\mcp-servers\hypercode-mcp-server.py")) { $missingFiles++ }

if ($missingFiles -gt 0) {
    Write-Host "❌ Missing critical files. Check the implementation summary." -ForegroundColor Red
} else {
    Write-Host "✅ All critical files present" -ForegroundColor Green
}

# 3. Check Python & MCP
Write-Host "`n3. Checking Python & MCP..." -ForegroundColor Yellow
if (Test-Command "python") {
    $pythonVersion = python --version
    Write-Host "   $pythonVersion" -ForegroundColor Gray
    
    # Check for mcp package
    try {
        python -c "import mcp; print('MCP package found')" > $null 2>&1
        Write-Host "✅ Python 'mcp' package installed" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Python 'mcp' package NOT found." -ForegroundColor Yellow
        Write-Host "   Run: pip install mcp" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ Python not found." -ForegroundColor Red
}

# 4. Check Local Model
Write-Host "`n4. Checking Local Model (smollm2)..." -ForegroundColor Yellow
$modelCheck = docker model list 2>&1 | Select-String "smollm2"
if ($modelCheck) {
    Write-Host "✅ smollm2 model found" -ForegroundColor Green
} else {
    Write-Host "⚠️  smollm2 model NOT found." -ForegroundColor Yellow
    Write-Host "   Run: docker model pull smollm2" -ForegroundColor Gray
}

Write-Host "`n========================================"
Write-Host "🎉 Validation Complete!" -ForegroundColor Cyan
Write-Host "Next Steps:"
Write-Host "1. Install MCP: pip install mcp"
Write-Host "2. Pull Model: docker model pull smollm2"
Write-Host "3. Run Test: See PANTHEON_INTEGRATION_GUIDE.md"
