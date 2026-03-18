#!/usr/bin/env bash
set -euo pipefail

sandbox="${NEMOCLAW_SANDBOX:-broski}"

command -v nemoclaw >/dev/null
command -v openclaw >/dev/null

nemoclaw "$sandbox" status >/dev/null
key_ok="false"
if [ -n "${NVIDIA_API_KEY:-}" ]; then
  key_ok="true"
fi

if [ "$key_ok" = "true" ]; then
  echo "ok: NemoClaw reachable; NVIDIA_API_KEY present (value not printed)"
else
  echo "ok: NemoClaw reachable; NVIDIA_API_KEY not detected in environment"
fi
