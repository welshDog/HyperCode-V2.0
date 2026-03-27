"""
HyperHealth — Seed Foundational Checks
Registers the 5 core checks into HyperHealth API.

Usage (from repo root):
    python agents/hyperhealth/seed_checks.py

Or via Docker:
    docker exec hyperhealth-api python seed_checks.py
"""
import httpx
import os
import sys
import json

API_BASE = os.environ.get("HYPERHEALTH_URL", "http://localhost:8095")
API_KEY  = os.environ.get("API_KEY", "")

if not API_KEY:
    # Try reading from .env in cwd
    try:
        for line in open(".env"):
            line = line.strip()
            if line.startswith("API_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    except FileNotFoundError:
        pass

if not API_KEY:
    print("\u274c ERROR: API_KEY not found. Set it as env var or ensure .env exists.")
    sys.exit(1)

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# ── The 5 foundational checks ──────────────────────────────────────────────────
CHECKS = [
    {
        "name": "hypercode-core-health",
        "type": "http",
        "target": "http://hypercode-core:8000/health",
        "environment": "production",
        "interval_seconds": 30,
        "thresholds": {
            "latency_ms": {"warn": 500, "crit": 2000, "window": 60}
        },
        "tags": ["core", "api", "critical"]
    },
    {
        "name": "healer-agent-health",
        "type": "http",
        "target": "http://healer-agent:8008/health",
        "environment": "production",
        "interval_seconds": 30,
        "thresholds": {
            "latency_ms": {"warn": 500, "crit": 2000, "window": 60}
        },
        "tags": ["healer", "self-heal", "critical"]
    },
    {
        "name": "grafana-health",
        "type": "http",
        "target": "http://grafana:3000/api/health",
        "environment": "production",
        "interval_seconds": 60,
        "thresholds": {
            "latency_ms": {"warn": 1000, "crit": 5000, "window": 120}
        },
        "tags": ["observability", "grafana"]
    },
    {
        "name": "redis-cache-health",
        "type": "cache",
        "target": "redis://redis:6379/0",
        "environment": "production",
        "interval_seconds": 20,
        "thresholds": {
            "latency_ms": {"warn": 100, "crit": 500, "window": 60}
        },
        "tags": ["cache", "redis", "critical"]
    },
    {
        "name": "postgres-db-health",
        "type": "db",
        # Uses the internal DSN — worker resolves this via asyncpg
        "target": os.environ.get(
            "DATABASE_URL",
            "postgresql://postgres:postgres@postgres:5432/hypercode"
        ).replace("postgresql+asyncpg://", "postgresql://"),
        "environment": "production",
        "interval_seconds": 30,
        "thresholds": {
            "latency_ms": {"warn": 200, "crit": 1000, "window": 60}
        },
        "tags": ["database", "postgres", "critical"]
    },
]


def seed():
    print(f"\n\U0001f9e0 HyperHealth Seed Script")
    print(f"\U0001f3af API: {API_BASE}")
    print(f"\U0001f511 Key: {API_KEY[:8]}...\n")

    created = 0
    skipped = 0
    failed  = 0

    with httpx.Client(base_url=API_BASE, headers=HEADERS, timeout=15) as client:
        # Get existing checks to avoid duplicates
        existing_resp = client.get("/checks", params={"enabled_only": False})
        existing_names = set()
        if existing_resp.status_code == 200:
            existing_names = {c["name"] for c in existing_resp.json()}

        for check in CHECKS:
            if check["name"] in existing_names:
                print(f"  \u23ed\ufe0f  SKIP  {check['name']} (already exists)")
                skipped += 1
                continue

            resp = client.post("/checks", json=check)

            if resp.status_code == 201:
                data = resp.json()
                print(f"  \u2705 CREATED  {data['name']}  [{data['type']}]  every {data['interval_seconds']}s  id={data['id'][:8]}...")
                created += 1
            else:
                print(f"  \u274c FAILED   {check['name']}  status={resp.status_code}  {resp.text}")
                failed += 1

    print(f"\n\U0001f4ca Results: {created} created | {skipped} skipped | {failed} failed")

    if created > 0:
        print("\n\U0001f525 Workers will start executing checks within 30s!")
        print("\U0001f4c8 Grafana metrics: http://localhost:3001")
        print("\U0001f9ea Health report:   curl -H \"X-API-Key: $API_KEY\" http://localhost:8095/health/report")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    seed()
