# HyperCode V2.0 Launch Verification Script (PowerShell)
# Usage: ./scripts/verify_launch.ps1

Write-Host "🚀 Initiating Launch Verification Sequence..." -ForegroundColor Cyan

# Helper to check URL with SSL bypass
function Test-Url {
    param($Url, $Name)
    Write-Host -NoNewline "Checking $Name ($Url)... "
    try {
        # Use Invoke-WebRequest with -SkipCertificateCheck for PowerShell 7+ / Core support
        # Use GET method as some endpoints (like FastAPI) might not explicitly support HEAD or return 405
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -SkipCertificateCheck -ErrorAction Stop
        $code = [int]$response.StatusCode
        
        if ($code -ge 200 -and $code -lt 400) {
            Write-Host "✅ ONLINE ($code)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ FAILED ($code)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ FAILED ($($_.Exception.Message))" -ForegroundColor Red
        return $false
    }
}

# 1. Verify Nginx
Test-Url "https://localhost/health" "Nginx Gateway"

# 2. Verify Core API
Test-Url "https://localhost/api/health" "HyperCode Core API"

# 3. Verify Frontend
Test-Url "https://localhost/" "Broski Terminal"

# 4. Verify Grafana
Test-Url "https://localhost/grafana/login" "Grafana Monitoring"

# 5. Database Check
Write-Host -NoNewline "Checking Database (postgres)... "
$dbStatus = docker exec postgres pg_isready -U hyper
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ ONLINE" -ForegroundColor Green
} else {
    Write-Host "❌ FAILED" -ForegroundColor Red
}

# 6. Redis Check
Write-Host -NoNewline "Checking Cache (redis)... "
$redisStatus = docker exec redis redis-cli ping
if ($redisStatus -match "PONG") {
    Write-Host "✅ ONLINE" -ForegroundColor Green
} else {
    Write-Host "❌ FAILED" -ForegroundColor Red
}

# 7. Agent Swarm Check
Write-Host "Checking Agent Swarm Containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.State}}" | Select-String "crew-orchestrator|project-strategist|frontend-specialist" | ForEach-Object {
    Write-Host $_
}

Write-Host "🏁 Verification Complete." -ForegroundColor Cyan
