$ErrorActionPreference = "Stop"

$sandbox = $env:NEMOCLAW_SANDBOX
if (-not $sandbox) { $sandbox = "broski" }

$script = @"
set -euo pipefail
cd '/mnt/h/HyperStation zone/HyperCode/HyperCode-V2.0'
export NEMOCLAW_SANDBOX='$sandbox'
export PATH="\$HOME/.nvm/versions/node/v22.22.1/bin:\$PATH"
bash scripts/nemoclaw/onboard.sh
"@

wsl -d Ubuntu-22.04 bash -lc $script

