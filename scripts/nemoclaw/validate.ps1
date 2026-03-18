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

$script = @"
set -euo pipefail
command -v nemoclaw >/dev/null
command -v openclaw >/dev/null
nemoclaw $sandbox status >/dev/null
echo ok
"@

$out = wsl bash -lc $script
if ($out -notmatch "ok") {
  throw "NemoClaw validation failed"
}

Write-Host "ok: NemoClaw is reachable and sandbox status works"

