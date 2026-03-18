$ErrorActionPreference = "Stop"

function Require-Command($name) {
  $cmd = Get-Command $name -ErrorAction SilentlyContinue
  if (-not $cmd) {
    throw "Missing required command: $name"
  }
}

Require-Command "wsl"

$sandbox = $env:NEMOCLAW_SANDBOX
if (-not $sandbox) { $sandbox = "broski" }

Write-Host "Validating NemoClaw sandbox: $sandbox"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
$envPath = Join-Path $repoRoot ".env"
$nvidiaApiKey = $env:NVIDIA_API_KEY
if (-not $nvidiaApiKey -and (Test-Path $envPath)) {
  $line = Select-String -Path $envPath -Pattern '^\s*NVIDIA_API_KEY\s*=\s*(.+)\s*$' -CaseSensitive
  if ($line) {
    $nvidiaApiKey = ($line.Matches[0].Groups[1].Value).Trim()
  }
}

$keyOk = [bool]($nvidiaApiKey -and $nvidiaApiKey.Trim().Length -gt 0)

$script = @"
set -euo pipefail
command -v nemoclaw >/dev/null
command -v openclaw >/dev/null
nemoclaw $sandbox status >/dev/null
echo ok
"@

$out = if ($keyOk) {
  wsl env NVIDIA_API_KEY="$nvidiaApiKey" bash -lc $script
} else {
  wsl bash -lc $script
}
if ($out -notmatch "ok") {
  throw "NemoClaw validation failed"
}

if ($keyOk) {
  Write-Host "ok: NemoClaw reachable; NVIDIA_API_KEY present (value not printed)"
} else {
  Write-Host "ok: NemoClaw reachable; NVIDIA_API_KEY not detected in environment"
}
