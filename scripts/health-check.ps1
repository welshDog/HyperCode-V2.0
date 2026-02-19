# Docker Health Check Script for HyperCode V2.0
# Checks status of all containers and reports issues

Write-Host "[HyperCode Docker Health Check]" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker ps > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Docker is not installed or not accessible." -ForegroundColor Red
    exit 1
}

# Get all containers
# Using --format "{{json .}}" to ensure valid JSON lines, then slurp them into an array
$containersRaw = docker ps -a --format "{{json .}}"
$containers = $containersRaw | ForEach-Object { $_ | ConvertFrom-Json }

if (-not $containers) {
    Write-Host "No containers found." -ForegroundColor Yellow
    exit 0
}

Write-Host "Container Status Summary:" -ForegroundColor Yellow
Write-Host ""

$runningCount = 0
$healthyCount = 0
$unhealthyCount = 0
$exitedCount = 0

foreach ($container in $containers) {
    $name = $container.Names
    $status = $container.Status
    $state = $container.State
    
    # Determine icon and color
    if ($state -eq "running") {
        $runningCount++
        if ($status -match "\(healthy\)") {
            $healthyCount++
            $icon = "[OK]"
            $color = "Green"
        } elseif ($status -match "\(unhealthy\)") {
            $unhealthyCount++
            $icon = "[FAIL]"
            $color = "Red"
        } else {
            $icon = "[RUN]"
            $color = "Green"
        }
    } elseif ($state -eq "exited") {
        $exitedCount++
        $icon = "[EXIT]"
        $color = "Red"
    } else {
        $icon = "[WARN]"
        $color = "Yellow"
    }
    
    Write-Host "$icon $name" -ForegroundColor $color -NoNewline
    Write-Host " - $status" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Running: $runningCount" -ForegroundColor Green
Write-Host "  Healthy: $healthyCount" -ForegroundColor Green
if ($unhealthyCount -gt 0) {
    Write-Host "  Unhealthy: $unhealthyCount" -ForegroundColor Red
}
if ($exitedCount -gt 0) {
    Write-Host "  Exited: $exitedCount" -ForegroundColor Red
}

Write-Host ""

# Check disk usage
Write-Host "Docker Disk Usage:" -ForegroundColor Yellow
docker system df

Write-Host ""

# Check unhealthy containers in detail
if ($unhealthyCount -gt 0) {
    Write-Host "Investigating Unhealthy Containers:" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($container in $containers) {
        if ($container.Status -match "unhealthy") {
            $name = $container.Names
            Write-Host "Logs for $name (last 20 lines):" -ForegroundColor Red
            docker logs --tail 20 $name
            Write-Host ""
        }
    }
}

# Check exited containers
if ($exitedCount -gt 0) {
    Write-Host "Exited Containers:" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($container in $containers) {
        if ($container.State -eq "exited") {
            $name = $container.Names
            Write-Host "Last logs for ${name}:" -ForegroundColor Gray
            docker logs --tail 10 $name
            Write-Host ""
        }
    }
    
    Write-Host "Tip: Run './scripts/cleanup-docker.ps1' to remove exited containers" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Health Check Complete!" -ForegroundColor Green
