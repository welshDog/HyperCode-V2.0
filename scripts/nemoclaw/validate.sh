#!/usr/bin/env bash
set -euo pipefail

sandbox="${NEMOCLAW_SANDBOX:-broski}"

command -v nemoclaw >/dev/null
command -v openclaw >/dev/null

nemoclaw "$sandbox" status >/dev/null
echo "ok: NemoClaw is reachable and sandbox status works"

