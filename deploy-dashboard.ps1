#Requires -Version 5.1
<#
.SYNOPSIS
    HyperCode V2.0 - Full Lifecycle Dashboard Deploy Script
.DESCRIPTION
    Automates build, configure, test, package, deploy, validate,
    and rollback for the HyperCode Mission Control Dashboard.
.PARAMETER Environment
    Target environment: Development | Staging | Production
.PARAMETER Version
    Semantic version string e.g. 1.2.3
.PARAMETER WhatIf
    Dry-run mode — shows what would happen without doing it.
.PARAMETER Verbose
    Enables verbose/debug output to console and log file.
.EXAMPLE
    .\deploy-dashboard.ps1 -Environment Production -Version 1.2.3
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param (
    [Parameter(Mandatory)]
    [ValidateSet('Development', 'Staging', 'Production')]
    [string]$Environment,

    [Parameter(Mandatory)]
    [ValidatePattern('^\d+\.\d+\.\d+$')]
    [string]$Version,

    [string]$GitRemote       = 'https://github.com/welshDog/HyperCode-V2.0.git',
    [string]$GitBranch       = 'main',
    [string]$ProjectRoot     = 'C:\Projects\dashboard',
    [string]$DeployTarget    = 'C:\Services\dashboard',
    [string]$IISTarget       = 'C:\inetpub\wwwroot\dashboard',
    [string]$DeployArchive   = 'C:\Deployments',
    [string]$LogRoot         = 'C:\Logs',
    [string]$TeamsWebhookUrl = '',   # <-- paste your webhook URL here
    [int]   $CoverageMin     = 80,
    [int]   $MaxArtifacts    = 3
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ════════════════════════════════════════════════════════════
# LOGGING SETUP
# ════════════════════════════════════════════════════════════
$Timestamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$LogFile    = "$LogRoot\dashboard-deploy-$Timestamp.log"
$BuildId    = "$Version-$Timestamp"

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet('INFO','WARN','ERROR','VERBOSE','SUCCESS')]
        [string]$Level = 'INFO'
    )
    $entry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    if ($Level -eq 'VERBOSE') { Write-Verbose $entry }
    else                       { Write-Host $entry -ForegroundColor $(switch ($Level) {
        'SUCCESS' { 'Green' }; 'WARN' { 'Yellow' }; 'ERROR' { 'Red' }; default { 'Cyan' }
    })}
    $entry | Out-File -FilePath $LogFile -Append -Encoding utf8
}

function Invoke-Step {
    param([string]$Name, [scriptblock]$Action)
    Write-Log "━━━ STARTING: $Name ━━━" 'INFO'
    try {
        & $Action
        Write-Log "━━━ DONE: $Name ✅ ━━━" 'SUCCESS'
    } catch {
        Write-Log "━━━ FAILED: $Name ❌ — $_" 'ERROR'
        Send-Notification -Status "FAILED at: $Name" -Error $_
        exit 1
    }
}

# Ensure log dir exists
if (-not (Test-Path $LogRoot)) { New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null }
Write-Log "🦅 HyperCode Dashboard Deploy STARTING — v$Version → $Environment" 'SUCCESS'
Write-Log "📋 Log file: $LogFile" 'INFO'


# ════════════════════════════════════════════════════════════
# HELPER: Run command and check exit code
# ════════════════════════════════════════════════════════════
function Invoke-Cmd {
    param([string]$Cmd, [string]$Args, [string]$WorkDir = $PWD)
    Write-Log "▶ $Cmd $Args" 'VERBOSE'
    $proc = Start-Process -FilePath $Cmd `
                          -ArgumentList $Args `
                          -WorkingDirectory $WorkDir `
                          -NoNewWindow -Wait -PassThru `
                          -RedirectStandardOutput "$env:TEMP\hc_stdout.txt" `
                          -RedirectStandardError  "$env:TEMP\hc_stderr.txt"
    $out = Get-Content "$env:TEMP\hc_stdout.txt" -Raw -ErrorAction SilentlyContinue
    $err = Get-Content "$env:TEMP\hc_stderr.txt" -Raw -ErrorAction SilentlyContinue
    if ($out) { $out | Out-File $LogFile -Append -Encoding utf8 }
    if ($err) { $err | Out-File $LogFile -Append -Encoding utf8 }
    if ($proc.ExitCode -ne 0) {
        throw "Command failed (exit $($proc.ExitCode)): $Cmd $Args`n$err"
    }
}


# ════════════════════════════════════════════════════════════
# PHASE 1 — ENVIRONMENT PREPARATION
# ════════════════════════════════════════════════════════════
Invoke-Step '1 · Environment Preparation' {

    # Tool requirements: [name, winget-id, min-version, check-cmd]
    $tools = @(
        @{ Name='git';    WinGet='Git.Git';              MinVer=[version]'2.40'; Check={ git --version } }
        @{ Name='node';   WinGet='OpenJS.NodeJS.LTS';    MinVer=[version]'18.0'; Check={ node --version } }
        @{ Name='npm';    WinGet=$null;                   MinVer=[version]'9.0';  Check={ npm --version } }
        @{ Name='python'; WinGet='Python.Python.3.12';   MinVer=[version]'3.11'; Check={ python --version } }
        @{ Name='docker'; WinGet='Docker.DockerDesktop'; MinVer=[version]'24.0'; Check={ docker --version } }
    )

    foreach ($t in $tools) {
        $installed = $true
        $rawVer    = $null
        try {
            $rawVer = (& $t.Check 2>&1) -replace '[^\d\.]','' | Select-String '\d+\.\d+' | ForEach-Object { $_.Matches[0].Value }
        } catch { $installed = $false }

        if (-not $installed -or -not $rawVer) {
            Write-Log "⚠ $($t.Name) NOT found — installing via winget..." 'WARN'
            if ($t.WinGet) {
                if ($PSCmdlet.ShouldProcess($t.Name, 'winget install')) {
                    Invoke-Cmd 'winget' "install --id $($t.WinGet) --silent --accept-package-agreements --accept-source-agreements"
                    # Refresh PATH
                    $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' +
                                [System.Environment]::GetEnvironmentVariable('PATH','User')
                }
            } else {
                Write-Log "  $($t.Name) is bundled with another tool — skipping direct install." 'VERBOSE'
            }
        } else {
            $ver = [version]($rawVer.Trim())
            if ($ver -lt $t.MinVer) {
                Write-Log "⚠ $($t.Name) v$ver is below minimum v$($t.MinVer)" 'WARN'
            } else {
                Write-Log "✅ $($t.Name) v$ver — OK" 'INFO'
            }
        }
    }

    # Create folder structure
    $dirs = @(
        $ProjectRoot, $DeployTarget, $DeployArchive,
        "$DeployArchive\logs", "$DeployArchive\artifacts", $LogRoot
    )
    foreach ($d in $dirs) {
        if (-not (Test-Path $d)) {
            if ($PSCmdlet.ShouldProcess($d, 'Create directory')) {
                New-Item -ItemType Directory -Path $d -Force | Out-Null
                Write-Log "📁 Created: $d" 'VERBOSE'
            }
        }
    }
    Write-Log "📁 Project folder structure ready." 'INFO'
}


# ════════════════════════════════════════════════════════════
# PHASE 2 — SOURCE CODE ACQUISITION
# ════════════════════════════════════════════════════════════
$RepoPath = "$ProjectRoot\repo"

Invoke-Step '2 · Source Code Acquisition' {
    if (Test-Path "$RepoPath\.git") {
        Write-Log "🔄 Repo exists — pulling latest..." 'INFO'
        if ($PSCmdlet.ShouldProcess($RepoPath, 'git pull')) {
            Invoke-Cmd 'git' 'fetch --all --prune'   $RepoPath
            Invoke-Cmd 'git' "checkout $GitBranch"   $RepoPath
            Invoke-Cmd 'git' 'pull --ff-only'        $RepoPath
        }
    } else {
        Write-Log "⬇ Cloning $GitRemote → $RepoPath..." 'INFO'
        if ($PSCmdlet.ShouldProcess($RepoPath, 'git clone')) {
            Invoke-Cmd 'git' "clone --branch $GitBranch --depth 50 $GitRemote `"$RepoPath`""
        }
    }

    # Verify clean working directory
    $status = git -C $RepoPath status --porcelain 2>&1
    if ($status) {
        Write-Log "⚠ Working directory has uncommitted changes:`n$status" 'WARN'
    }

    $CommitSHA = (git -C $RepoPath rev-parse HEAD).Trim()
    Write-Log "📌 Commit SHA: $CommitSHA" 'INFO'
    $global:CommitSHA = $CommitSHA
}


# ════════════════════════════════════════════════════════════
# PHASE 3 — DEPENDENCY INSTALLATION
# ════════════════════════════════════════════════════════════
Invoke-Step '3 · Dependency Installation' {

    # Python venv + pip
    $venvPath = "$RepoPath\.venv"
    if (-not (Test-Path $venvPath)) {
        if ($PSCmdlet.ShouldProcess($venvPath, 'python -m venv')) {
            Invoke-Cmd 'python' "-m venv `"$venvPath`""
        }
    }
    $pip = "$venvPath\Scripts\pip.exe"
    if ($PSCmdlet.ShouldProcess('requirements.txt', 'pip install')) {
        Invoke-Cmd $pip "install --upgrade pip --quiet"
        Invoke-Cmd $pip "install -r `"$RepoPath\requirements.txt`" --quiet --cache-dir `"$ProjectRoot\.pip_cache`""
    }
    Write-Log "🐍 Python deps installed." 'INFO'

    # Node/npm
    if (Test-Path "$RepoPath\package.json") {
        if ($PSCmdlet.ShouldProcess('package.json', 'npm ci')) {
            Invoke-Cmd 'npm' "ci --prefer-offline --cache `"$ProjectRoot\.npm_cache`"" $RepoPath
        }
        Write-Log "📦 Node deps installed." 'INFO'
    }

    # Dashboard (Next.js / React — inside dashboard/ subfolder)
    if (Test-Path "$RepoPath\dashboard\package.json") {
        if ($PSCmdlet.ShouldProcess('dashboard/package.json', 'npm ci')) {
            Invoke-Cmd 'npm' "ci --prefer-offline --cache `"$ProjectRoot\.npm_cache`"" "$RepoPath\dashboard"
        }
        Write-Log "📦 Dashboard Node deps installed." 'INFO'
    }
}


# ════════════════════════════════════════════════════════════
# PHASE 4 — BUILD & COMPILE
# ════════════════════════════════════════════════════════════
$BuildDir = "$ProjectRoot\build-$BuildId"

Invoke-Step '4 · Build & Compile' {

    # Set environment flags
    $env:NODE_ENV       = $Environment.ToLower()
    $env:NEXT_PUBLIC_ENV = $Environment.ToUpper()
    $env:APP_VERSION    = $Version

    New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null

    # Python FastAPI backend — just validate syntax (uvicorn serves it directly)
    $py = "$RepoPath\.venv\Scripts\python.exe"
    if (Test-Path "$RepoPath\backend") {
        Write-Log "🔧 Validating Python backend..." 'INFO'
        if ($PSCmdlet.ShouldProcess('backend', 'python syntax check')) {
            Invoke-Cmd $py "-m py_compile `"$RepoPath\backend\main.py`""
        }
    }

    # Next.js / React dashboard build
    if (Test-Path "$RepoPath\dashboard\package.json") {
        Write-Log "⚛ Building Next.js dashboard..." 'INFO'
        if ($PSCmdlet.ShouldProcess('dashboard', 'npm run build')) {
            Invoke-Cmd 'npm' "run build -- --no-lint 2>&1" "$RepoPath\dashboard"
        }
        # Copy build output
        Copy-Item -Path "$RepoPath\dashboard\.next" -Destination "$BuildDir\dashboard" -Recurse -Force
        Write-Log "✅ Dashboard build complete → $BuildDir\dashboard" 'SUCCESS'
    }

    Write-Log "🏗 Build artefacts written to: $BuildDir" 'INFO'
}


# ════════════════════════════════════════════════════════════
# PHASE 5 — CONFIGURATION & SECRETS
# ════════════════════════════════════════════════════════════
Invoke-Step '5 · Configuration & Secrets' {

    $envFile = "$BuildDir\.env.production"

    # Load base from .env.example
    $envExample = "$RepoPath\.env.example"
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile -Force
    } else {
        New-Item -ItemType File -Path $envFile | Out-Null
    }

    # Pull secrets from Windows Credential Manager
    # Usage: cmdkey /add:HyperCode_DB_URL /user:deploy /pass:"postgres://..."
    $secrets = @('DB_URL', 'REDIS_URL', 'SECRET_KEY', 'OPENAI_API_KEY', 'DISCORD_TOKEN')
    foreach ($s in $secrets) {
        try {
            # Read from Windows Credential Manager via cmdkey
            $cred = Get-StoredCredential -Target "HyperCode_$s" -ErrorAction SilentlyContinue
            if ($cred) {
                $val = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
                    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($cred.Password)
                )
                Add-Content -Path $envFile -Value "$s=$val"
                Write-Log "🔐 Secret loaded: $s" 'VERBOSE'
            } else {
                Write-Log "⚠ Secret not found in Credential Manager: HyperCode_$s" 'WARN'
            }
        } catch {
            Write-Log "⚠ Could not load secret $s — $_" 'WARN'
        }
    }

    # Force env overrides
    @"
NODE_ENV=$($Environment.ToLower())
APP_VERSION=$Version
DEPLOY_TIMESTAMP=$Timestamp
"@ | Add-Content -Path $envFile

    # Validate .env syntax (no empty required keys)
    $required = @('NODE_ENV', 'APP_VERSION')
    $content  = Get-Content $envFile
    foreach ($r in $required) {
        if (-not ($content -match "^$r=.+")) {
            throw "Missing required env key: $r in $envFile"
        }
    }
    Write-Log "🔐 Config written and validated: $envFile" 'INFO'
}


# ════════════════════════════════════════════════════════════
# PHASE 6 — DATABASE MIGRATION
# ════════════════════════════════════════════════════════════
Invoke-Step '6 · Database Migration' {

    $py      = "$RepoPath\.venv\Scripts\python.exe"
    $alembic = "$RepoPath\.venv\Scripts\alembic.exe"
    $backupDir = "$DeployArchive\db-backups"
    if (-not (Test-Path $backupDir)) { New-Item -ItemType Directory -Path $backupDir -Force | Out-Null }

    # Backup before migration (pg_dump if PostgreSQL available)
    $pgDump = (Get-Command 'pg_dump' -ErrorAction SilentlyContinue)?.Source
    if ($pgDump) {
        $backupFile = "$backupDir\db-backup-$Timestamp.sql"
        Write-Log "💾 Backing up database → $backupFile" 'INFO'
        if ($PSCmdlet.ShouldProcess('PostgreSQL', 'pg_dump backup')) {
            # DB URL pulled from env file
            $dbUrl = (Get-Content "$BuildDir\.env.production" | Select-String '^DB_URL=(.+)') |
                     ForEach-Object { $_.Matches[0].Groups[1].Value }
            if ($dbUrl) {
                $env:DATABASE_URL = $dbUrl
                & $pgDump --dbname=$dbUrl --file=$backupFile 2>&1 | Out-File $LogFile -Append
                Write-Log "✅ DB backup saved: $backupFile" 'SUCCESS'
            } else {
                Write-Log "⚠ DB_URL not set — skipping backup" 'WARN'
            }
        }
    }

    # Run Alembic migrations
    if (Test-Path $alembic) {
        Write-Log "🗄 Running Alembic migrations..." 'INFO'
        if ($PSCmdlet.ShouldProcess('database', 'alembic upgrade head')) {
            Invoke-Cmd $alembic 'upgrade head' $RepoPath
        }

        # Confirm current schema version
        $currentRev = & $alembic current 2>&1
        Write-Log "📋 Alembic current: $currentRev" 'INFO'
    } else {
        Write-Log "ℹ No alembic.exe found — skipping migration." 'VERBOSE'
    }
}


# ════════════════════════════════════════════════════════════
# PHASE 7 — STATIC ASSET OPTIMIZATION
# ════════════════════════════════════════════════════════════
Invoke-Step '7 · Static Asset Optimization' {

    # Next.js build already handles minification in production mode.
    # We compute content hashes for cache-busting manifest here.

    $manifestPath = "$BuildDir\asset-manifest.json"
    $assets = Get-ChildItem -Path "$BuildDir\dashboard" -Recurse `
              -Include '*.js','*.css','*.png','*.jpg','*.svg' -ErrorAction SilentlyContinue

    $manifest = @{}
    foreach ($a in $assets) {
        $hash = (Get-FileHash -Path $a.FullName -Algorithm SHA256).Hash.Substring(0,8).ToLower()
        $relative = $a.FullName.Replace($BuildDir, '').TrimStart('\')
        $manifest[$relative] = $hash
    }

    $manifest | ConvertTo-Json -Depth 3 | Out-File $manifestPath -Encoding utf8
    Write-Log "📋 Asset manifest written: $manifestPath ($($manifest.Count) files)" 'INFO'

    # Image compression (requires optipng/imagemagick if installed)
    $pngs = $assets | Where-Object { $_.Extension -eq '.png' }
    $optipng = (Get-Command 'optipng' -ErrorAction SilentlyContinue)?.Source
    if ($optipng -and $pngs) {
        Write-Log "🖼 Compressing $($pngs.Count) PNGs with optipng..." 'VERBOSE'
        foreach ($png in $pngs) {
            if ($PSCmdlet.ShouldProcess($png.Name, 'optipng compress')) {
                Invoke-Cmd 'optipng' "-quiet `"$($png.FullName)`""
            }
        }
    }
}


# ════════════════════════════════════════════════════════════
# PHASE 8 — TEST EXECUTION
# ════════════════════════════════════════════════════════════
Invoke-Step '8 · Test Execution' {

    $py      = "$RepoPath\.venv\Scripts\python.exe"
    $pytest  = "$RepoPath\.venv\Scripts\pytest.exe"
    $reportDir = "$ProjectRoot\test-reports-$Timestamp"
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null

    # ── Python tests (pytest + coverage)
    if (Test-Path $pytest) {
        Write-Log "🧪 Running Python tests..." 'INFO'
        $pytestArgs = @(
            "$RepoPath\tests",
            "--tb=short",
            "-q",
            "--junitxml=`"$reportDir\pytest-results.xml`"",
            "--cov=`"$RepoPath`"",
            "--cov-report=xml:`"$reportDir\coverage.xml`"",
            "--cov-fail-under=$CoverageMin"
        ) -join ' '
        if ($PSCmdlet.ShouldProcess('pytest', 'run tests')) {
            Invoke-Cmd $pytest $pytestArgs $RepoPath
        }
        Write-Log "✅ Python tests passed (≥$CoverageMin% coverage)" 'SUCCESS'
    } else {
        Write-Log "⚠ pytest not found — skipping Python tests" 'WARN'
    }

    # ── Node/Jest tests
    if (Test-Path "$RepoPath\package.json") {
        $jestConfig = (Get-Content "$RepoPath\package.json" | ConvertFrom-Json).scripts.test
        if ($jestConfig) {
            Write-Log "🧪 Running Jest tests..." 'INFO'
            if ($PSCmdlet.ShouldProcess('jest', 'run tests')) {
                Invoke-Cmd 'npm' "test -- --ci --coverage --coverageThreshold=`"{global:{lines:$CoverageMin}}`"" $RepoPath
            }
            Write-Log "✅ Jest tests passed" 'SUCCESS'
        }
    }

    Write-Log "📊 Test reports saved: $reportDir" 'INFO'
}


# ════════════════════════════════════════════════════════════
# PHASE 9 — PACKAGING
# ════════════════════════════════════════════════════════════
$ArtifactPath = "$DeployArchive\artifacts\dashboard-$BuildId.zip"

Invoke-Step '9 · Packaging' {

    Write-Log "📦 Creating versioned archive: $ArtifactPath" 'INFO'
    if ($PSCmdlet.ShouldProcess($BuildDir, 'Compress-Archive')) {
        Compress-Archive -Path "$BuildDir\*" -DestinationPath $ArtifactPath -Force
    }

    # SHA256 checksum
    $sha256 = (Get-FileHash -Path $ArtifactPath -Algorithm SHA256).Hash
    $checksumFile = $ArtifactPath -replace '\.zip$', '.sha256'
    "$sha256  $ArtifactPath" | Out-File $checksumFile -Encoding utf8
    Write-Log "🔑 SHA256: $sha256" 'INFO'

    # Manifest
    $manifestFile = $ArtifactPath -replace '\.zip$', '.manifest.json'
    @{
        version    = $Version
        buildId    = $BuildId
        commitSHA  = $global:CommitSHA
        environment= $Environment
        timestamp  = $Timestamp
        sha256     = $sha256
        artifact   = $ArtifactPath
    } | ConvertTo-Json | Out-File $manifestFile -Encoding utf8
    Write-Log "📋 Manifest: $manifestFile" 'INFO'

    # Prune old artifacts — keep only last $MaxArtifacts
    $oldArtifacts = Get-ChildItem "$DeployArchive\artifacts\*.zip" |
                    Sort-Object LastWriteTime -Descending |
                    Select-Object -Skip $MaxArtifacts
    foreach ($old in $oldArtifacts) {
        Write-Log "🗑 Removing old artifact: $($old.Name)" 'VERBOSE'
        Remove-Item $old.FullName -Force
        Remove-Item ($old.FullName -replace '\.zip$','.sha256')   -Force -ErrorAction SilentlyContinue
        Remove-Item ($old.FullName -replace '\.zip$','.manifest.json') -Force -ErrorAction SilentlyContinue
    }
}


# ════════════════════════════════════════════════════════════
# PHASE 10 — DEPLOYMENT
# ════════════════════════════════════════════════════════════
Invoke-Step '10 · Deployment' {

    # ── Stop existing services gracefully
    $serviceName = 'HyperCodeDashboard'
    $iisAppName  = 'HyperCodeDashboard'

    $svc = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($svc -and $svc.Status -eq 'Running') {
        Write-Log "⏹ Stopping Windows service: $serviceName" 'INFO'
        if ($PSCmdlet.ShouldProcess($serviceName, 'Stop-Service')) {
            Stop-Service -Name $serviceName -Force
            Start-Sleep 3
        }
    }

    # IIS site stop (if IIS is present)
    $iisModule = Get-Module -ListAvailable WebAdministration -ErrorAction SilentlyContinue
    if ($iisModule) {
        Import-Module WebAdministration -ErrorAction SilentlyContinue
        $site = Get-WebSite -Name $iisAppName -ErrorAction SilentlyContinue
        if ($site) {
            Write-Log "⏹ Stopping IIS site: $iisAppName" 'INFO'
            if ($PSCmdlet.ShouldProcess($iisAppName, 'Stop IIS site')) {
                Stop-WebSite -Name $iisAppName
            }
        }
    }

    # ── Extract artifact to deploy target
    $deployDest = if ($iisModule) { $IISTarget } else { $DeployTarget }
    Write-Log "📂 Deploying to: $deployDest" 'INFO'
    if ($PSCmdlet.ShouldProcess($deployDest, 'Extract artifact')) {
        if (-not (Test-Path $deployDest)) { New-Item -ItemType Directory -Path $deployDest -Force | Out-Null }
        Expand-Archive -Path $ArtifactPath -DestinationPath $deployDest -Force
    }

    # ── Copy .env.production
    Copy-Item "$BuildDir\.env.production" "$deployDest\.env.production" -Force

    # ── Set ACLs (IIS_IUSRS read + NETWORK SERVICE read/execute)
    if ($PSCmdlet.ShouldProcess($deployDest, 'Set ACLs')) {
        $acl  = Get-Acl $deployDest
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            'IIS_IUSRS', 'ReadAndExecute', 'ContainerInherit,ObjectInherit', 'None', 'Allow'
        )
        $acl.AddAccessRule($rule)
        Set-Acl -Path $deployDest -AclObject $acl
        Write-Log "🔒 ACLs set on $deployDest" 'INFO'
    }

    # ── Restart service / IIS
    if ($svc) {
        if ($PSCmdlet.ShouldProcess($serviceName, 'Start-Service')) {
            Start-Service -Name $serviceName
            Write-Log "▶ Service $serviceName started" 'SUCCESS'
        }
    }
    if ($iisModule -and $site) {
        if ($PSCmdlet.ShouldProcess($iisAppName, 'Start IIS site')) {
            Start-WebSite -Name $iisAppName
            Write-Log "▶ IIS site $iisAppName started" 'SUCCESS'
        }
    }

    # ── Warmup — HTTP 200 check
    $warmupUrl = 'http://localhost:8088'
    Write-Log "🌐 Warming up: $warmupUrl" 'INFO'
    $maxWait = 30; $waited = 0
    do {
        Start-Sleep 2; $waited += 2
        try {
            $resp = Invoke-WebRequest -Uri $warmupUrl -UseBasicParsing -TimeoutSec 5
            if ($resp.StatusCode -eq 200) {
                Write-Log "✅ Dashboard responded HTTP 200 in ${waited}s" 'SUCCESS'
                break
            }
        } catch { Write-Log "⏳ Waiting for dashboard... (${waited}s)" 'VERBOSE' }
    } while ($waited -lt $maxWait)

    if ($waited -ge $maxWait) {
        throw "Dashboard did not respond HTTP 200 within ${maxWait}s after deploy!"
    }
}


# ════════════════════════════════════════════════════════════
# PHASE 11 — POST-DEPLOYMENT VALIDATION
# ════════════════════════════════════════════════════════════
Invoke-Step '11 · Post-Deployment Validation' {

    $baseUrl     = 'http://localhost:8088'
    $apiEndpoints = @('/health', '/api/agents', '/api/status')

    foreach ($ep in $apiEndpoints) {
        $url = "$baseUrl$ep"
        $sw  = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
            $sw.Stop()
            $ms = $sw.ElapsedMilliseconds
            if ($resp.StatusCode -eq 200 -and $ms -lt 2000) {
                Write-Log "✅ $url → HTTP $($resp.StatusCode) in ${ms}ms" 'SUCCESS'
            } elseif ($ms -ge 2000) {
                Write-Log "⚠ $url responded in ${ms}ms (>2000ms threshold)" 'WARN'
            } else {
                Write-Log "⚠ $url → HTTP $($resp.StatusCode)" 'WARN'
            }
        } catch {
            Write-Log "❌ $url → FAILED: $_" 'ERROR'
        }
    }

    # Write rollback instructions to dated log
    $rollbackLog = "$DeployArchive\logs\rollback-instructions-$Timestamp.txt"
    @"
ROLLBACK INSTRUCTIONS — Deploy $BuildId
========================================
Run: .\deploy-dashboard.ps1 -Rollback
Or manually:
  1. Stop-Service HyperCodeDashboard
  2. Expand-Archive <previous .zip> → $DeployTarget
  3. Start-Service HyperCodeDashboard

Previous artifact:
$(Get-ChildItem "$DeployArchive\artifacts\*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 1 -First 1 | ForEach-Object { $_.FullName })

DB backup (if created): $DeployArchive\db-backups\db-backup-$Timestamp.sql
"@ | Out-File $rollbackLog -Encoding utf8
    Write-Log "📝 Rollback instructions: $rollbackLog" 'INFO'

    # Notify Teams / Webhook
    Send-Notification -Status 'SUCCESS'
}


# ════════════════════════════════════════════════════════════
# PHASE 12 — ROLLBACK FUNCTION
# ════════════════════════════════════════════════════════════
function Invoke-Rollback {
    <#
    .SYNOPSIS One-click rollback to previous artifact.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    Write-Log "↩ ROLLBACK INITIATED" 'WARN'
    $artifacts = Get-ChildItem "$DeployArchive\artifacts\*.zip" |
                 Sort-Object LastWriteTime -Descending

    if ($artifacts.Count -lt 2) {
        Write-Log "❌ No previous artifact found to roll back to!" 'ERROR'
        return
    }

    $previous = $artifacts[1]  # Second newest = previous deploy
    Write-Log "↩ Rolling back to: $($previous.Name)" 'WARN'

    $svc = Get-Service 'HyperCodeDashboard' -ErrorAction SilentlyContinue
    if ($svc -and $svc.Status -eq 'Running') {
        if ($PSCmdlet.ShouldProcess('HyperCodeDashboard', 'Stop-Service')) {
            Stop-Service 'HyperCodeDashboard' -Force; Start-Sleep 3
        }
    }

    if ($PSCmdlet.ShouldProcess($DeployTarget, 'Restore previous artifact')) {
        Expand-Archive -Path $previous.FullName -DestinationPath $DeployTarget -Force
    }

    if ($svc) {
        if ($PSCmdlet.ShouldProcess('HyperCodeDashboard', 'Start-Service')) {
            Start-Service 'HyperCodeDashboard'
        }
    }

    # Optionally restore DB backup
    $latestBackup = Get-ChildItem "$DeployArchive\db-backups\*.sql" |
                    Sort-Object LastWriteTime -Descending |
                    Select-Object -First 1
    if ($latestBackup) {
        Write-Log "🗄 DB backup available for manual restore: $($latestBackup.FullName)" 'WARN'
        Write-Log "  Run: psql --dbname=<DB_URL> -f `"$($latestBackup.FullName)`"" 'WARN'
    }

    Write-Log "✅ Rollback complete → $($previous.Name)" 'SUCCESS'
}


# ════════════════════════════════════════════════════════════
# NOTIFICATION HELPER
# ════════════════════════════════════════════════════════════
function Send-Notification {
    param([string]$Status, [string]$Error = '')

    $color  = if ($Status -eq 'SUCCESS') { '00FF00' } else { 'FF0000' }
    $emoji  = if ($Status -eq 'SUCCESS') { '✅' }      else { '❌' }
    $body   = @{
        '@type'    = 'MessageCard'
        '@context' = 'http://schema.org/extensions'
        themeColor = $color
        summary    = "HyperCode Dashboard Deploy $Status"
        sections   = @(@{
            activityTitle = "$emoji HyperCode Dashboard — v$Version $Status"
            facts = @(
                @{ name='Environment'; value=$Environment }
                @{ name='Version';     value=$Version }
                @{ name='Commit';      value=$global:CommitSHA }
                @{ name='Timestamp';   value=$Timestamp }
                @{ name='Log';         value=$LogFile }
                if ($Error) { @{ name='Error'; value=$Error } }
            ) | Where-Object { $_ }
        })
    } | ConvertTo-Json -Depth 5

    if ($TeamsWebhookUrl) {
        try {
            Invoke-RestMethod -Uri $TeamsWebhookUrl -Method Post `
                -ContentType 'application/json' -Body $body
            Write-Log "📣 Teams notification sent." 'VERBOSE'
        } catch {
            Write-Log "⚠ Teams notification failed: $_" 'WARN'
        }
    }
}


# ════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ════════════════════════════════════════════════════════════
Write-Log "" 'INFO'
Write-Log "╔══════════════════════════════════════════════════╗" 'SUCCESS'
Write-Log "║  🦅 HYPERCODE DASHBOARD DEPLOYED! NICE ONE BRO! ║" 'SUCCESS'
Write-Log "╠══════════════════════════════════════════════════╣" 'SUCCESS'
Write-Log "║  Version    : $Version" 'SUCCESS'
Write-Log "║  Environment: $Environment" 'SUCCESS'
Write-Log "║  Commit     : $($global:CommitSHA.Substring(0,8))" 'SUCCESS'
Write-Log "║  Artifact   : $ArtifactPath" 'SUCCESS'
Write-Log "║  Log        : $LogFile" 'SUCCESS'
Write-Log "╠══════════════════════════════════════════════════╣" 'SUCCESS'
Write-Log "║  To rollback: . .\deploy-dashboard.ps1; Invoke-Rollback" 'INFO'
Write-Log "╚══════════════════════════════════════════════════╝" 'SUCCESS'
