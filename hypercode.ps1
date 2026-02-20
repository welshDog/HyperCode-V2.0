#!/usr/bin/env pwsh
<#
.SYNOPSIS
    HyperCode Orchestrator - Intelligent startup, monitoring, and management
.DESCRIPTION
    Manages HyperCode services with smart dependency ordering, health checks,
    retry logic, and centralized health monitoring.
.PARAMETER Action
    start   - Start all services (default)
    stop    - Stop all services
    restart - Restart all services
    status  - Show health status of all services
    logs    - Stream logs (optional: specify service name)
    clean   - Remove dangling images/volumes
    agents  - Start agents only (with --profile agents)
.PARAMETER Service
    Optional service name for logs (e.g., 'hypercode-core', 'frontend-specialist')
.EXAMPLE
    .\hypercode.ps1 start
    .\hypercode.ps1 status
    .\hypercode.ps1 logs frontend-specialist
#>

param(
    [string]$Action = "start",
    [string]$Service = "",
    [switch]$Agents = $false
)

$ErrorActionPreference = "Stop"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-Status {
    param([string]$Message, [string]$Color = $Blue)
    Write-Host "$Color$Message$Reset"
}

function Write-Success {
    param([string]$Message)
    Write-Host "$Green✓ $Message$Reset"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "$Red✗ $Message$Reset"
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "$Yellow⚠ $Message$Reset"
}

# Check prerequisites
function Check-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    $commands = @("docker", "docker-compose")
    foreach ($cmd in $commands) {
        if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
            Write-Error-Custom "$cmd not found. Please install Docker Desktop."
            exit 1
        }
    }
    
    if (-not (Test-Path ".env")) {
        Write-Error-Custom ".env file not found. Please copy .env.example to .env and configure it."
        exit 1
    }
    
    Write-Success "Prerequisites OK"
}

# Build images with caching
function Build-Images {
    Write-Status "Building images with layer caching..."
    
    $profile = if ($Agents) { "--profile agents" } else { "" }
    $cmd = "docker-compose -f docker-compose.yml $profile build --pull"
    
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Build failed"
        exit 1
    }
    
    Write-Success "Build complete"
}

# Start services with intelligent ordering
function Start-Services {
    Write-Status "Starting HyperCode services..."
    
    # Stage 1: Infrastructure (Redis, Postgres, Jaeger)
    Write-Status "Stage 1: Infrastructure..."
    $infra_services = @("redis", "postgres", "jaeger")
    foreach ($svc in $infra_services) {
        Write-Status "  ↳ $svc"
        docker-compose -f docker-compose.yml up -d $svc 2>&1 | Out-Null
    }
    
    # Wait for infrastructure to be healthy
    Write-Status "Waiting for infrastructure health..."
    Start-Sleep -Seconds 5
    docker-compose -f docker-compose.yml ps | grep -E "(redis|postgres|jaeger)" | ForEach-Object {
        if ($_ -match "unhealthy|exited") {
            Write-Error-Custom "Infrastructure service failed: $_"
            exit 1
        }
    }
    Write-Success "Infrastructure ready"
    
    # Stage 2: Core services
    Write-Status "Stage 2: Core services..."
    $core_services = @("hypercode-core", "prometheus", "grafana")
    foreach ($svc in $core_services) {
        Write-Status "  ↳ $svc"
        docker-compose -f docker-compose.yml up -d $svc 2>&1 | Out-Null
    }
    
    # Wait for core
    Write-Status "Waiting for core service health..."
    $max_retries = 30
    $retry = 0
    while ($retry -lt $max_retries) {
        $health = docker-compose -f docker-compose.yml ps hypercode-core | grep -c "healthy"
        if ($health -gt 0) {
            Write-Success "Core service healthy"
            break
        }
        $retry++
        Start-Sleep -Seconds 2
    }
    
    if ($retry -eq $max_retries) {
        Write-Error-Custom "Core service failed to become healthy"
        docker-compose -f docker-compose.yml logs hypercode-core | tail -50
        exit 1
    }
    
    # Stage 3: Frontend & Workers
    Write-Status "Stage 3: Frontend & workers..."
    $stage3_services = @("broski-terminal", "hyperflow-editor", "celery-worker", "hafs-service", "dashboard")
    foreach ($svc in $stage3_services) {
        Write-Status "  ↳ $svc"
        docker-compose -f docker-compose.yml up -d $svc 2>&1 | Out-Null
    }
    
    # Stage 4: Agents (optional)
    if ($Agents) {
        Write-Status "Stage 4: Agents..."
        $agent_services = @("crew-orchestrator", "frontend-specialist", "security-engineer", "system-architect")
        foreach ($svc in $agent_services) {
            Write-Status "  ↳ $svc"
            docker-compose -f docker-compose.yml --profile agents up -d $svc 2>&1 | Out-Null
        }
        
        # Wait for agents
        Write-Status "Waiting for agents..."
        Start-Sleep -Seconds 10
    }
    
    Write-Success "All services started!"
    Write-Status "Dashboard: $Blue http://localhost:8088 $Reset"
    Write-Status "Terminal: $Blue http://localhost:3000 $Reset"
    Write-Status "Grafana: $Blue http://localhost:3001 $Reset"
    Write-Status "Jaeger: $Blue http://localhost:16686 $Reset"
}

# Show centralized health status
function Show-Status {
    Write-Status "`n=== HyperCode Health Status ===$Reset`n"
    
    $containers = docker-compose -f docker-compose.yml ps --format "{{.Names}}|{{.Status}}"
    $running = 0
    $unhealthy = 0
    $exited = 0
    
    $containers | ForEach-Object {
        if ($_ -match "^\|" -or $_ -eq "") { return }
        
        $name, $status = $_ -split '\|'
        $status_lower = $status.ToLower()
        
        if ($status_lower -match "healthy|up") {
            Write-Host "$Green✓$Reset $name - $status"
            $running++
        }
        elseif ($status_lower -match "unhealthy") {
            Write-Host "$Red✗$Reset $name - $status"
            $unhealthy++
        }
        else {
            Write-Host "$Yellow⚠$Reset $name - $status"
            $exited++
        }
    }
    
    Write-Status "`n=== Summary ===$Reset"
    Write-Host "Running: $Green$running$Reset | Unhealthy: $Red$unhealthy$Reset | Exited: $Yellow$exited$Reset"
    
    if ($unhealthy -gt 0) {
        Write-Warning-Custom "Some services are unhealthy. Run '.\hypercode.ps1 logs <service>' for details"
    }
}

# Stream logs
function Show-Logs {
    if ($Service) {
        Write-Status "Streaming logs for $Service..."
        docker-compose -f docker-compose.yml logs -f $Service
    }
    else {
        Write-Status "Streaming logs for all services..."
        docker-compose -f docker-compose.yml logs -f
    }
}

# Stop services
function Stop-Services {
    Write-Status "Stopping services..."
    docker-compose -f docker-compose.yml down
    Write-Success "Services stopped"
}

# Restart services
function Restart-Services {
    Stop-Services
    Start-Sleep -Seconds 2
    Start-Services
}

# Clean up
function Clean-System {
    Write-Status "Cleaning up Docker..."
    docker system prune -a --volumes --force
    Write-Success "Cleanup complete"
}

# Main dispatcher
Check-Prerequisites

switch ($Action.ToLower()) {
    "start" {
        Build-Images
        Start-Services
        Show-Status
    }
    "stop" {
        Stop-Services
    }
    "restart" {
        Restart-Services
        Show-Status
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs
    }
    "clean" {
        Clean-System
    }
    "agents" {
        Build-Images
        Start-Services -Agents $true
        Show-Status
    }
    default {
        Write-Error-Custom "Unknown action: $Action"
        Write-Status "Usage: .\hypercode.ps1 [start|stop|restart|status|logs|clean|agents]"
        exit 1
    }
}
