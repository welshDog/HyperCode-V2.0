"""
HyperHealth Orchestrator API
FastAPI service — health checks, reports, Prometheus metrics.

Endpoints:
  GET  /health              — liveness (no auth)
  GET  /checks              — list check definitions
  POST /checks              — create check definition
  GET  /checks/{id}         — get single check
  DELETE /checks/{id}       — delete check
  GET  /checks/{id}/results — recent results for a check
  GET  /health/report       — aggregated health report
  GET  /metrics             — Prometheus text format
  POST /selfheal/trigger    — manually trigger self-heal
"""
from __future__ import annotations

import os
import time
import uuid
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional

import structlog
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    Counter, Gauge, Histogram, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, func

from models import (
    Base,
    CheckDefinitionORM, CheckResultORM, AlertPolicyORM, SelfHealPolicyORM,
    CheckDefinitionCreate, CheckDefinitionOut, CheckResultOut, HealthReportOut
)

# ── Structured logging ───────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger("hyperhealth.api")

# ── Config ───────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable must be set")

# asyncpg dialect
ASYNC_DB_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

API_KEY = os.environ.get("API_KEY", "")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable must be set")

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
HEALER_URL = os.environ.get("HEALER_URL", "http://healer-agent:8008")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# ── Prometheus metrics ───────────────────────────────────────────────────────
REGISTRY = CollectorRegistry(auto_describe=True)

CHECK_STATUS = Gauge(
    "hyperhealth_check_status",
    "Current status of a health check (0=OK, 1=WARN, 2=CRIT)",
    ["check_name", "environment", "type"],
    registry=REGISTRY,
)
CHECK_LATENCY = Histogram(
    "hyperhealth_check_latency_ms",
    "Latency of health check execution in milliseconds",
    ["check_name", "type"],
    buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000],
    registry=REGISTRY,
)
INCIDENTS_OPEN = Gauge(
    "hyperhealth_incidents_open",
    "Number of currently open incidents",
    ["severity", "environment"],
    registry=REGISTRY,
)
SELFHEALS_TOTAL = Counter(
    "hyperhealth_selfheals_executed_total",
    "Total self-heal actions executed",
    ["action", "service"],
    registry=REGISTRY,
)
SELFHEALS_FAILED = Counter(
    "hyperhealth_selfheals_failed_total",
    "Total self-heal actions that failed",
    ["action", "service"],
    registry=REGISTRY,
)

# ── DB Engine ─────────────────────────────────────────────────────────────────
engine = create_async_engine(
    ASYNC_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("hyperhealth.startup", environment=ENVIRONMENT, healer_url=HEALER_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _validate_healer_connection()
    yield
    await engine.dispose()
    log.info("hyperhealth.shutdown")


async def _validate_healer_connection():
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{HEALER_URL}/health")
            if resp.status_code == 200:
                log.info("healer.reachable", url=HEALER_URL)
            else:
                log.warning("healer.unhealthy", status=resp.status_code)
    except Exception as exc:
        log.warning("healer.unreachable", error=str(exc), msg="Self-heal disabled until Healer is reachable")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="HyperHealth",
    description="Comprehensive health monitoring & self-healing for HyperCode V2.0",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Auth dependency ───────────────────────────────────────────────────────────
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# ── DB dependency ────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# ── Status helpers ───────────────────────────────────────────────────────────
def status_to_int(status: str) -> int:
    return {"OK": 0, "WARN": 1, "CRIT": 2}.get(status, 3)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    """Liveness endpoint — no auth required."""
    return {
        "status": "ok",
        "service": "hyperhealth",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/checks", response_model=List[CheckDefinitionOut], tags=["Checks"])
async def list_checks(
    environment: Optional[str] = Query(None),
    enabled_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """List all check definitions, optionally filtered by environment."""
    stmt = select(CheckDefinitionORM)
    if environment:
        stmt = stmt.where(CheckDefinitionORM.environment == environment)
    if enabled_only:
        stmt = stmt.where(CheckDefinitionORM.enabled.is_(True))
    result = await db.execute(stmt)
    return result.scalars().all()


@app.post("/checks", response_model=CheckDefinitionOut, status_code=201, tags=["Checks"])
async def create_check(
    payload: CheckDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Create a new health check definition."""
    check = CheckDefinitionORM(
        id=uuid.uuid4(),
        name=payload.name,
        type=payload.type,
        target=payload.target,
        environment=payload.environment,
        interval_seconds=payload.interval_seconds,
        thresholds={k: v.model_dump() for k, v in payload.thresholds.items()},
        alert_policy_id=payload.alert_policy_id,
        self_heal_policy_id=payload.self_heal_policy_id,
        tags=payload.tags,
        enabled=payload.enabled,
    )
    db.add(check)
    await db.commit()
    await db.refresh(check)
    log.info("check.created", check_id=str(check.id), name=check.name, type=check.type)
    return check


@app.get("/checks/{check_id}", response_model=CheckDefinitionOut, tags=["Checks"])
async def get_check(
    check_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Get a single check definition by ID."""
    result = await db.execute(select(CheckDefinitionORM).where(CheckDefinitionORM.id == check_id))
    check = result.scalar_one_or_none()
    if not check:
        raise HTTPException(status_code=404, detail="Check not found")
    return check


@app.delete("/checks/{check_id}", status_code=204, tags=["Checks"])
async def delete_check(
    check_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Disable (soft-delete) a check definition."""
    result = await db.execute(select(CheckDefinitionORM).where(CheckDefinitionORM.id == check_id))
    check = result.scalar_one_or_none()
    if not check:
        raise HTTPException(status_code=404, detail="Check not found")
    check.enabled = False
    await db.commit()
    log.info("check.disabled", check_id=str(check_id))


@app.get("/checks/{check_id}/results", response_model=List[CheckResultOut], tags=["Results"])
async def get_check_results(
    check_id: uuid.UUID,
    limit: int = Query(default=50, le=500),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Get recent results for a specific check."""
    stmt = (
        select(CheckResultORM)
        .where(CheckResultORM.check_id == check_id)
        .order_by(CheckResultORM.started_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@app.get("/health/report", response_model=HealthReportOut, tags=["Reports"])
async def get_health_report(
    env: str = Query(default="prod"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Aggregate recent check results into a full health report for an environment."""
    since = datetime.utcnow() - timedelta(minutes=10)

    # Count results by status in last 10 minutes
    stmt = (
        select(CheckResultORM.status, func.count(CheckResultORM.id))
        .where(
            CheckResultORM.environment == env,
            CheckResultORM.started_at >= since,
        )
        .group_by(CheckResultORM.status)
    )
    rows = (await db.execute(stmt)).all()
    status_counts = {row[0]: row[1] for row in rows}

    total = sum(status_counts.values())
    overall = "OK"
    if status_counts.get("CRIT", 0) > 0:
        overall = "CRIT"
    elif status_counts.get("WARN", 0) > 0:
        overall = "WARN"

    # Top incidents = most recent CRIT results
    crit_stmt = (
        select(CheckResultORM)
        .where(
            CheckResultORM.environment == env,
            CheckResultORM.status == "CRIT",
            CheckResultORM.started_at >= since,
        )
        .order_by(CheckResultORM.started_at.desc())
        .limit(5)
    )
    crits = (await db.execute(crit_stmt)).scalars().all()
    top_incidents = [
        {"check_id": str(c.check_id), "message": c.message, "at": c.started_at.isoformat()}
        for c in crits
    ]

    recommendations = []
    if status_counts.get("CRIT", 0) > 0:
        recommendations.append("Investigate CRIT checks immediately — self-heal may be triggered")
    if status_counts.get("WARN", 0) > 2:
        recommendations.append("Multiple WARN conditions — review thresholds or capacity")
    if total == 0:
        recommendations.append("No check results in last 10 minutes — verify workers are running")

    return HealthReportOut(
        environment=env,
        generated_at=datetime.utcnow(),
        total_checks=total,
        status_counts=status_counts,
        overall_status=overall,
        top_incidents=top_incidents,
        self_heals_last_hour=0,  # TODO: wire to SelfHeal audit table
        mttr_seconds=None,
        recommendations=recommendations,
    )


@app.get("/metrics", tags=["Observability"])
async def metrics():
    """Expose Prometheus metrics for scraping by Grafana/Prometheus."""
    data = generate_latest(REGISTRY)
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/selfheal/trigger", tags=["SelfHeal"])
async def trigger_selfheal(
    service: str = Query(...),
    action: str = Query(default="restart"),
    env: str = Query(default="prod"),
    _: str = Depends(verify_api_key),
):
    """Manually trigger a self-heal action via Healer Agent."""
    import httpx
    payload = {
        "agent_name": service,
        "action": action,
        "environment": env,
        "source": "hyperhealth-manual",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{HEALER_URL}/heal", json=payload)
            resp.raise_for_status()
            SELFHEALS_TOTAL.labels(action=action, service=service).inc()
            log.info("selfheal.triggered", service=service, action=action, env=env)
            return {"status": "triggered", "service": service, "action": action, "healer_response": resp.json()}
    except Exception as exc:
        SELFHEALS_FAILED.labels(action=action, service=service).inc()
        log.error("selfheal.failed", service=service, error=str(exc))
        raise HTTPException(status_code=502, detail=f"Healer Agent unreachable: {exc}")
