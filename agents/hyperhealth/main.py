"""
HyperHealth Orchestrator API
FastAPI service — health checks, reports, Prometheus metrics.
"""
from __future__ import annotations

import os
import uuid
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
    CheckDefinitionORM, CheckResultORM,
    CheckDefinitionCreate, CheckDefinitionOut, CheckResultOut, HealthReportOut
)

# ── Structured logging — FIXED: no add_logger_name (incompatible with PrintLogger) ─────
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()

# ── Config ─────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable must be set")

# Safe dialect swap — only replace if not already asyncpg
ASYNC_DB_URL = (
    DATABASE_URL
    if "asyncpg" in DATABASE_URL
    else DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
)

API_KEY = os.environ.get("API_KEY", "")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable must be set")

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
HEALER_URL = os.environ.get("HEALER_URL", "http://healer-agent:8008")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# ── Prometheus metrics ───────────────────────────────────────────────────────
REGISTRY = CollectorRegistry(auto_describe=False)

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
    log.info("hyperhealth.db_tables_ready")
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
        log.warning("healer.unreachable", error=str(exc))


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="HyperHealth",
    description="Comprehensive health monitoring & self-healing for HyperCode V2.0",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Auth ──────────────────────────────────────────────────────────────────────
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


def status_to_int(status: str) -> int:
    return {"OK": 0, "WARN": 1, "CRIT": 2}.get(status, 3)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
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
    log.info("check.created", check_id=str(check.id), name=check.name)
    return check


@app.get("/checks/{check_id}", response_model=CheckDefinitionOut, tags=["Checks"])
async def get_check(
    check_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_api_key),
):
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
    since = datetime.utcnow() - timedelta(minutes=10)
    stmt = (
        select(CheckResultORM.status, func.count(CheckResultORM.id))
        .where(CheckResultORM.environment == env, CheckResultORM.started_at >= since)
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

    crit_stmt = (
        select(CheckResultORM)
        .where(CheckResultORM.environment == env, CheckResultORM.status == "CRIT",
               CheckResultORM.started_at >= since)
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
        recommendations.append("Investigate CRIT checks — self-heal may be triggered")
    if status_counts.get("WARN", 0) > 2:
        recommendations.append("Multiple WARNs — review thresholds or capacity")
    if total == 0:
        recommendations.append("No results in last 10 min — are workers running?")

    return HealthReportOut(
        environment=env,
        generated_at=datetime.utcnow(),
        total_checks=total,
        status_counts=status_counts,
        overall_status=overall,
        top_incidents=top_incidents,
        self_heals_last_hour=0,
        mttr_seconds=None,
        recommendations=recommendations,
    )


@app.get("/metrics", tags=["Observability"])
async def metrics():
    data = generate_latest(REGISTRY)
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.post("/selfheal/trigger", tags=["SelfHeal"])
async def trigger_selfheal(
    service: str = Query(...),
    action: str = Query(default="restart"),
    env: str = Query(default="prod"),
    _: str = Depends(verify_api_key),
):
    import httpx
    payload = {"agent_name": service, "action": action, "environment": env, "source": "hyperhealth-manual"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{HEALER_URL}/heal", json=payload)
            resp.raise_for_status()
            SELFHEALS_TOTAL.labels(action=action, service=service).inc()
            log.info("selfheal.triggered", service=service, action=action)
            return {"status": "triggered", "service": service, "action": action, "healer_response": resp.json()}
    except Exception as exc:
        SELFHEALS_FAILED.labels(action=action, service=service).inc()
        log.error("selfheal.failed", service=service, error=str(exc))
        raise HTTPException(status_code=502, detail=f"Healer Agent unreachable: {exc}")
