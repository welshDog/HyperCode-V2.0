#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
env_path="$root/.env"
sandbox="${NEMOCLAW_SANDBOX:-broski}"

command -v nemoclaw >/dev/null
echo "PASS: nemoclaw on PATH"
command -v openclaw >/dev/null
echo "PASS: openclaw on PATH"

nemoclaw "$sandbox" status >/dev/null
echo "PASS: NemoClaw sandbox reachable ($sandbox)"

if [ -z "${NVIDIA_API_KEY:-}" ]; then
  if [ -f "$env_path" ]; then
    value="$(grep -E '^[[:space:]]*NVIDIA_API_KEY[[:space:]]*=' "$env_path" | head -n 1 | sed -E 's/^[[:space:]]*NVIDIA_API_KEY[[:space:]]*=[[:space:]]*//')"
    value="$(echo -n "$value" | tr -d '\r' | xargs || true)"
    if [ -n "$value" ]; then
      export NVIDIA_API_KEY="$value"
    fi
  fi
fi

if [ -n "${NVIDIA_API_KEY:-}" ]; then
  echo "PASS: NVIDIA_API_KEY present (value not printed)"
else
  echo "FAIL: NVIDIA_API_KEY not detected in environment" >&2
  exit 1
fi

echo "PASS: validate.sh complete"
