#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$root"

env_path="$root/.env"
logs_dir="$root/logs/nemoclaw"
mkdir -p "$logs_dir"

sandbox="${NEMOCLAW_SANDBOX:-broski}"

if [ -d "$HOME/.nvm/versions/node" ]; then
  latest="$(ls -1 "$HOME/.nvm/versions/node" | sort -V | tail -n 1)"
  if [ -n "$latest" ]; then
    export PATH="$HOME/.nvm/versions/node/$latest/bin:$PATH"
  fi
fi

if [ ! -f "$env_path" ]; then
  echo "ERROR: Missing .env at repo root" >&2
  exit 1
fi

key="$(grep -E '^[[:space:]]*NVIDIA_API_KEY[[:space:]]*=' "$env_path" | head -n 1 | sed -E 's/^[[:space:]]*NVIDIA_API_KEY[[:space:]]*=[[:space:]]*//')"
key="$(echo -n "$key" | tr -d '\r' | xargs || true)"
if [ -z "${key}" ]; then
  echo "ERROR: NVIDIA_API_KEY missing/empty in .env (value not printed)" >&2
  exit 1
fi

export NVIDIA_API_KEY="$key"

ts="$(date -u +%Y%m%dT%H%M%SZ)"
log="$logs_dir/onboard-$ts.log"

printf "%s\n" "info: onboarding NemoClaw sandbox '$sandbox' (log: $log)"

printf "%b" "$sandbox\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n" | nemoclaw onboard >"$log" 2>&1

tail -n 30 "$log"
