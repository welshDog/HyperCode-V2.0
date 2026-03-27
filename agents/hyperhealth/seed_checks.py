"""
HyperHealth — Seed Foundational Checks
Registers the 5 core checks into HyperHealth API.

Usage (from repo root):
    python agents/hyperhealth/seed_checks.py
    python agents/hyperhealth/seed_checks.py --force   # re-create existing checks
"""
import httpx
import os
import sys

API_BASE = os.environ.get("HYPERHEALTH_URL", "http://localhost:8095")
API_KEY  = os.environ.get("API_KEY", "")
FORCE    = "--force" in sys.argv

# ── Load .env if needed ───────────────────────────────────────────────────────────
def load_env(path=".env"):
    env = {}
    try:
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env

dot_env = load_env()

if not API_KEY:
    API_KEY = dot_env.get("API_KEY", "")
if not API_KEY:
    print("\u274c ERROR: API_KEY not found in env or .env")
    sys.exit(1)

# ── Resolve the real DB DSN ────────────────────────────────────────────────────────────
def resolve_db_dsn() -> str:
    # Priority: HYPERCODE_DB_URL > DATABASE_URL > constructed from parts
    dsn = (
        os.environ.get("HYPERCODE_DB_URL")
        or dot_env.get("HYPERCODE_DB_URL")
        or os.environ.get("DATABASE_URL")
        or dot_env.get("DATABASE_URL")
    )
    if dsn:
        # Strip asyncpg dialect — worker uses asyncpg directly
        return dsn.replace("postgresql+asyncpg://", "postgresql://")

    # Construct from parts
    user = dot_env.get("POSTGRES_USER", "postgres")
    pwd  = dot_env.get("POSTGRES_PASSWORD", "postgres")
    db   = dot_env.get("POSTGRES_DB", "hypercode")
    return f"postgresql://{user}:{pwd}@postgres:5432/{db}"

DB_DSN = resolve_db_dsn()
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# ── Check definitions ───────────────────────────────────────────────────────────────
CHECKS = [
    {
        "name": "hypercode-core-health",
        "type": "http",
        "target": "http://hypercode-core:8000/health",
        "environment": "production",
        "interval_seconds": 30,
        "thresholds": {"latency_ms": {"warn": 500, "crit": 2000, "window": 60}},
        "tags": ["core", "api", "critical"],
    },
    {
        "name": "healer-agent-health",
        "type": "http",
        "target": "http://healer-agent:8008/health",
        "environment": "production",
        "interval_seconds": 30,
        "thresholds": {"latency_ms": {"warn": 500, "crit": 2000, "window": 60}},
        "tags": ["healer", "self-heal", "critical"],
    },
    {
        "name": "grafana-health",
        "type": "http",
        "target": "http://grafana:3000/api/health",
        "environment": "production",
        "interval_seconds": 60,
        "thresholds": {"latency_ms": {"warn": 1000, "crit": 5000, "window": 120}},
        "tags": ["observability", "grafana"],
    },
    {
        "name": "redis-cache-health",
        "type": "cache",
        "target": "redis://redis:6379/0",
        "environment": "production",
        "interval_seconds": 20,
        "thresholds": {"latency_ms": {"warn": 100, "crit": 500, "window": 60}},
        "tags": ["cache", "redis", "critical"],
    },
    {
        "name": "postgres-db-health",
        "type": "db",
        "target": DB_DSN,
        "environment": "production",
        "interval_seconds": 30,
        "thresholds": {"latency_ms": {"warn": 200, "crit": 1000, "window": 60}},
        "tags": ["database", "postgres", "critical"],
    },
]


def seed():
    print(f"\n\U0001f9e0 HyperHealth Seed Script{'  [--force mode]' if FORCE else ''}")
    print(f"\U0001f3af API : {API_BASE}")
    print(f"\U0001f511 Key : {API_KEY[:8]}...")
    print(f"\U0001f5c4\ufe0f  DB  : {DB_DSN[:50]}...\n")

    created = skipped = failed = updated = 0

    with httpx.Client(base_url=API_BASE, headers=HEADERS, timeout=15) as client:
        existing_resp = client.get("/checks", params={"enabled_only": False})
        existing = {}
        if existing_resp.status_code == 200:
            for c in existing_resp.json():
                existing[c["name"]] = c["id"]

        for check in CHECKS:
            name = check["name"]
            exists = name in existing

            if exists and not FORCE:
                print(f"  \u23ed\ufe0f  SKIP     {name} (already exists — use --force to update)")
                skipped += 1
                continue

            if exists and FORCE:
                # Soft-delete old then recreate
                del_resp = client.delete(f"/checks/{existing[name]}")
                if del_resp.status_code not in (200, 204):
                    print(f"  \u26a0\ufe0f  WARN     could not delete old {name}: {del_resp.status_code}")

            resp = client.post("/checks", json=check)
            if resp.status_code == 201:
                data = resp.json()
                verb = "UPDATED" if exists else "CREATED"
                print(f"  \u2705 {verb:<8} {data['name']}  [{data['type']}]  every {data['interval_seconds']}s  id={data['id'][:8]}...")
                created += 1
                if exists:
                    updated += 1
            else:
                print(f"  \u274c FAILED   {name}  status={resp.status_code}  {resp.text}")
                failed += 1

    total_new = created - updated
    print(f"\n\U0001f4ca Results: {total_new} created | {updated} updated | {skipped} skipped | {failed} failed")

    if created > 0:
        print("\n\U0001f525 Workers will start executing checks within 30s!")
        print("\U0001f4c8 Grafana :  http://localhost:3001")
        print("\U0001f9ea Report  :  curl -H \"X-API-Key: $API_KEY\" http://localhost:8095/health/report?env=production")
        print("\U0001f4ca Metrics :  curl http://localhost:8095/metrics")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    seed()
