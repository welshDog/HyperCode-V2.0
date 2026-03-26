"""
HyperHealth Async Worker
Runs all health checks concurrently, stores results, triggers alerts + self-heal.
"""
import asyncio
import json
import os
import ssl
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import asyncpg
import httpx
import redis.asyncio as aioredis

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://hypercode:hypercode@postgres:5432/hypercode")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
HEALER_URL = os.getenv("HEALER_URL", "http://healer-agent:8008")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL", "")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "200"))


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class CheckDef:
    id: UUID
    name: str
    type: str
    target: str
    environment: str
    interval_seconds: int
    thresholds: Dict[str, Any]
    self_heal_policy_id: Optional[int]
    next_run_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CheckResult:
    check_id: UUID
    status: str  # OK | WARN | CRIT
    latency_ms: float
    value: Optional[float]
    message: str
    environment: str


# ---------------------------------------------------------------------------
# Check executors
# ---------------------------------------------------------------------------
async def execute_http_check(check: CheckDef, client: httpx.AsyncClient) -> CheckResult:
    start = time.monotonic()
    try:
        resp = await client.get(check.target, timeout=10)
        latency = (time.monotonic() - start) * 1000
        t = check.thresholds.get("latency_ms", {"warn": 500, "crit": 2000})
        if resp.status_code >= 500:
            status = "CRIT"
        elif resp.status_code >= 400 or latency > t.get("crit", 2000):
            status = "CRIT"
        elif latency > t.get("warn", 500):
            status = "WARN"
        else:
            status = "OK"
        return CheckResult(
            check_id=check.id, status=status, latency_ms=latency,
            value=float(resp.status_code), message=f"HTTP {resp.status_code} {latency:.1f}ms",
            environment=check.environment,
        )
    except Exception as e:
        latency = (time.monotonic() - start) * 1000
        return CheckResult(
            check_id=check.id, status="CRIT", latency_ms=latency,
            value=None, message=f"HTTP check failed: {e}",
            environment=check.environment,
        )


async def execute_db_check(check: CheckDef, db: asyncpg.Pool) -> CheckResult:
    start = time.monotonic()
    try:
        await db.fetchval("SELECT 1")
        latency = (time.monotonic() - start) * 1000
        t = check.thresholds.get("latency_ms", {"warn": 100, "crit": 500})
        status = "CRIT" if latency > t.get("crit", 500) else (
            "WARN" if latency > t.get("warn", 100) else "OK"
        )
        return CheckResult(
            check_id=check.id, status=status, latency_ms=latency,
            value=latency, message=f"DB ping {latency:.1f}ms",
            environment=check.environment,
        )
    except Exception as e:
        return CheckResult(
            check_id=check.id, status="CRIT", latency_ms=0,
            value=None, message=f"DB check failed: {e}",
            environment=check.environment,
        )


async def execute_redis_check(check: CheckDef, redis: aioredis.Redis) -> CheckResult:
    start = time.monotonic()
    try:
        await redis.ping()
        latency = (time.monotonic() - start) * 1000
        status = "CRIT" if latency > 200 else ("WARN" if latency > 50 else "OK")
        return CheckResult(
            check_id=check.id, status=status, latency_ms=latency,
            value=latency, message=f"Redis ping {latency:.1f}ms",
            environment=check.environment,
        )
    except Exception as e:
        return CheckResult(
            check_id=check.id, status="CRIT", latency_ms=0,
            value=None, message=f"Redis check failed: {e}",
            environment=check.environment,
        )


async def execute_tls_check(check: CheckDef, client: httpx.AsyncClient) -> CheckResult:
    """Check TLS cert expiry for HTTPS endpoints."""
    import ssl, socket
    from datetime import timezone
    try:
        host = check.target.replace("https://", "").replace("http://", "").split("/")[0]
        port = 443
        ctx = ssl.create_default_context()
        conn = ctx.wrap_socket(socket.socket(), server_hostname=host)
        conn.settimeout(5)
        conn.connect((host, port))
        cert = conn.getpeercert()
        conn.close()
        expiry_str = cert["notAfter"]
        expiry = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days_left = (expiry - datetime.now(timezone.utc)).days
        status = "CRIT" if days_left < 7 else ("WARN" if days_left < 30 else "OK")
        return CheckResult(
            check_id=check.id, status=status, latency_ms=0,
            value=float(days_left), message=f"TLS cert expires in {days_left} days",
            environment=check.environment,
        )
    except Exception as e:
        return CheckResult(
            check_id=check.id, status="CRIT", latency_ms=0,
            value=None, message=f"TLS check failed: {e}",
            environment=check.environment,
        )


async def execute_check(check: CheckDef, db: asyncpg.Pool, redis: aioredis.Redis, client: httpx.AsyncClient) -> CheckResult:
    """Dispatch check to correct executor based on type."""
    dispatch = {
        "http": lambda: execute_http_check(check, client),
        "db": lambda: execute_db_check(check, db),
        "cache": lambda: execute_redis_check(check, redis),
        "tls": lambda: execute_tls_check(check, client),
    }
    executor = dispatch.get(check.type)
    if executor:
        return await executor()
    # Default: HTTP check for unknown types
    return await execute_http_check(check, client)


# ---------------------------------------------------------------------------
# Store result + push to Prometheus via Redis pub/sub
# ---------------------------------------------------------------------------
async def store_result(result: CheckResult, db: asyncpg.Pool, redis: aioredis.Redis):
    rid = uuid4()
    await db.execute(
        """
        INSERT INTO check_results
            (id, check_id, status, latency_ms, value, message, environment, started_at, finished_at)
        VALUES ($1,$2,$3,$4,$5,$6,$7,NOW(),NOW())
        """,
        rid, result.check_id, result.status, result.latency_ms,
        result.value, result.message, result.environment,
    )
    # Cache latest result per check in Redis (fast dashboard reads)
    await redis.setex(
        f"hyperhealth:latest:{result.check_id}",
        120,
        json.dumps({
            "status": result.status,
            "latency_ms": result.latency_ms,
            "message": result.message,
            "at": datetime.now(timezone.utc).isoformat(),
        }),
    )


# ---------------------------------------------------------------------------
# Alerting
# ---------------------------------------------------------------------------
async def send_slack_alert(check_name: str, result: CheckResult):
    if not SLACK_WEBHOOK:
        return
    emoji = "🔴" if result.status == "CRIT" else "🟡"
    payload = {
        "text": f"{emoji} *HyperHealth [{result.status}]* — `{check_name}` in `{result.environment}`\n> {result.message}"
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(SLACK_WEBHOOK, json=payload, timeout=5)
    except Exception as e:
        print(f"Slack alert failed: {e}")


# ---------------------------------------------------------------------------
# Self-healing
# ---------------------------------------------------------------------------
async def trigger_self_heal(check: CheckDef, result: CheckResult, redis: aioredis.Redis):
    """Call Healer Agent to remediate a CRIT service."""
    # Rate-limit: only trigger once per 5 min per check
    cooldown_key = f"hyperhealth:heal_cooldown:{check.id}"
    if await redis.exists(cooldown_key):
        return

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{HEALER_URL}/heal",
                json={
                    "agent_name": check.name,
                    "agent_url": check.target,
                    "attempts": 3,
                    "timeout": 30,
                    "triggered_by": "hyperhealth",
                    "environment": check.environment,
                },
                timeout=15,
            )
        if resp.status_code < 300:
            print(f"🩹 Self-heal triggered for {check.name} ({check.environment})")
            await redis.setex(cooldown_key, 300, "1")  # 5min cooldown
        else:
            print(f"⚠️ Healer returned {resp.status_code} for {check.name}")
    except Exception as e:
        print(f"Self-heal call failed for {check.name}: {e}")


# ---------------------------------------------------------------------------
# CRIT failure tracker (triggers heal after N consecutive failures)
# ---------------------------------------------------------------------------
async def track_and_heal(check: CheckDef, result: CheckResult, redis: aioredis.Redis):
    if result.status != "CRIT":
        await redis.delete(f"hyperhealth:crit_streak:{check.id}")
        return

    streak_key = f"hyperhealth:crit_streak:{check.id}"
    streak = await redis.incr(streak_key)
    await redis.expire(streak_key, 300)

    if streak >= 3:
        print(f"🚨 {check.name} has {streak} consecutive CRITs — triggering self-heal")
        await trigger_self_heal(check, result, redis)
        await send_slack_alert(check.name, result)


# ---------------------------------------------------------------------------
# Main scheduler loop
# ---------------------------------------------------------------------------
async def load_checks(db: asyncpg.Pool) -> List[CheckDef]:
    rows = await db.fetch(
        "SELECT id, name, type, target, environment, interval_seconds, thresholds, self_heal_policy_id "
        "FROM check_definitions WHERE enabled = TRUE"
    )
    return [
        CheckDef(
            id=r["id"], name=r["name"], type=r["type"], target=r["target"],
            environment=r["environment"], interval_seconds=r["interval_seconds"],
            thresholds=json.loads(r["thresholds"]) if isinstance(r["thresholds"], str) else (r["thresholds"] or {}),
            self_heal_policy_id=r["self_heal_policy_id"],
        )
        for r in rows
    ]


async def run_worker():
    print("⚡ HyperHealth Worker starting...")
    db = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=20)
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    semaphore = asyncio.Semaphore(WORKER_CONCURRENCY)

    async def safe_run(check: CheckDef, client: httpx.AsyncClient):
        async with semaphore:
            try:
                result = await execute_check(check, db, redis, client)
                await store_result(result, db, redis)
                await track_and_heal(check, result, redis)
                check.next_run_at = datetime.now(timezone.utc) + timedelta(seconds=check.interval_seconds)
            except Exception as e:
                print(f"Worker error for {check.name}: {e}")

    # Reload checks every 60s from DB
    checks: List[CheckDef] = []
    last_reload = datetime.now(timezone.utc) - timedelta(seconds=61)

    async with httpx.AsyncClient(timeout=10, limits=httpx.Limits(max_connections=500)) as client:
        while True:
            now = datetime.now(timezone.utc)

            # Reload check definitions periodically
            if (now - last_reload).total_seconds() > 60:
                checks = await load_checks(db)
                last_reload = now
                print(f"📋 Loaded {len(checks)} checks")

            # Dispatch all due checks concurrently
            due = [c for c in checks if c.next_run_at <= now]
            if due:
                await asyncio.gather(*[safe_run(c, client) for c in due])

            await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(run_worker())
