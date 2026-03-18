"""throttle-agent FastAPI service."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import docker
from docker.errors import DockerException, NotFound
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge, generate_latest
from pydantic import BaseModel

logger = logging.getLogger("throttle-agent")
logging.basicConfig(level=logging.INFO)

PROM_REGISTRY = CollectorRegistry()

THROTTLE_ACTIONS_TOTAL = Counter(
    "throttle_actions_total",
    "Throttle actions executed",
    ["tier", "action", "container"],
    registry=PROM_REGISTRY,
)
DOCKER_UP = Gauge(
    "throttle_docker_up",
    "Whether docker daemon is reachable from throttle-agent (1/0)",
    registry=PROM_REGISTRY,
)
SYSTEM_RAM_USAGE_PCT = Gauge(
    "throttle_system_ram_usage_pct",
    "Estimated total RAM usage percentage (containers sum / docker mem total)",
    registry=PROM_REGISTRY,
)

CONTAINER_STATE = Gauge(
    "throttle_container_state",
    "Container state as a gauge (labels include state)",
    ["name", "state"],
    registry=PROM_REGISTRY,
)
CONTAINER_RAM_BYTES = Gauge(
    "throttle_container_ram_bytes",
    "Container memory usage in bytes",
    ["name"],
    registry=PROM_REGISTRY,
)

DEFAULT_TIERS: dict[int, list[str]] = {
    1: ["postgres", "redis", "hypercode-core", "hypercode-ollama"],
    2: ["crew-orchestrator", "hypercode-dashboard"],
    3: ["celery-worker"],
    4: ["test-agent"],
    5: ["prometheus", "tempo", "loki", "grafana"],
    6: ["minio", "cadvisor", "node-exporter", "security-scanner"],
}


class TierContainerStatus(BaseModel):
    name: str
    status: str | None = None
    health: str | None = None
    ram_bytes: int | None = None
    error: str | None = None


class TierStatus(BaseModel):
    tier: int
    containers: list[TierContainerStatus]
    running: int
    healthy: int


def _docker_client() -> docker.DockerClient:
    return docker.from_env()


def _container_health(container: Any) -> str | None:
    state = container.attrs.get("State", {})
    health = state.get("Health")
    if isinstance(health, dict):
        status = health.get("Status")
        if isinstance(status, str):
            return status
    return None


def _container_state(container: Any) -> str | None:
    state = container.attrs.get("State", {})
    status = state.get("Status")
    if isinstance(status, str):
        return status
    return None


def _container_ram_bytes(container: Any) -> int | None:
    try:
        stats = container.stats(stream=False)
        mem = stats.get("memory_stats", {})
        usage = mem.get("usage")
        if isinstance(usage, int):
            return usage
        return None
    except Exception:
        return None


def _docker_mem_total_bytes(client: docker.DockerClient) -> int | None:
    try:
        info = client.api.info()
        mem_total = info.get("MemTotal")
        if isinstance(mem_total, int) and mem_total > 0:
            return mem_total
        return None
    except Exception:
        return None


def _estimate_system_ram_pct(client: docker.DockerClient, tiers: dict[int, list[str]]) -> float | None:
    mem_total = _docker_mem_total_bytes(client)
    if not mem_total:
        return None
    usage_sum = 0
    for _, names in tiers.items():
        for name in names:
            try:
                container = client.containers.get(name)
                ram = _container_ram_bytes(container)
                if isinstance(ram, int):
                    usage_sum += ram
            except Exception:
                continue
    return round((usage_sum / mem_total) * 100, 2)


def _reset_container_state_gauges(name: str) -> None:
    for state in ("created", "running", "paused", "restarting", "removing", "exited", "dead", "unknown"):
        try:
            CONTAINER_STATE.labels(name=name, state=state).set(0)
        except Exception:
            continue


def _record_container_metrics(status: TierContainerStatus) -> None:
    _reset_container_state_gauges(status.name)
    state = status.status or "unknown"
    CONTAINER_STATE.labels(name=status.name, state=state).set(1)
    if isinstance(status.ram_bytes, int):
        CONTAINER_RAM_BYTES.labels(name=status.name).set(status.ram_bytes)


def _get_tier_status(client: docker.DockerClient, tier: int, names: list[str]) -> TierStatus:
    containers: list[TierContainerStatus] = []
    running = 0
    healthy = 0

    for name in names:
        try:
            container = client.containers.get(name)
            container.reload()
            status = _container_state(container)
            health = _container_health(container)
            ram = _container_ram_bytes(container)
            if status == "running":
                running += 1
            if health == "healthy":
                healthy += 1
            containers.append(
                TierContainerStatus(name=name, status=status, health=health, ram_bytes=ram)
            )
        except NotFound:
            containers.append(TierContainerStatus(name=name, error="not_found"))
        except DockerException as e:
            containers.append(TierContainerStatus(name=name, error=str(e)))
        except Exception as e:
            containers.append(TierContainerStatus(name=name, error=str(e)))

    for c in containers:
        _record_container_metrics(c)

    return TierStatus(tier=tier, containers=containers, running=running, healthy=healthy)


def _get_tiers() -> dict[int, list[str]]:
    return DEFAULT_TIERS


def _parse_threshold(name: str, default: float) -> float:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


AUTO_THROTTLE_ENABLED = os.getenv("AUTO_THROTTLE_ENABLED", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
RAM_WARN_PCT = _parse_threshold("RAM_WARN_PCT", 80.0)
RAM_HIGH_PCT = _parse_threshold("RAM_HIGH_PCT", 90.0)
RAM_EMERGENCY_PCT = _parse_threshold("RAM_EMERGENCY_PCT", 95.0)
POLL_SECONDS = int(_parse_threshold("POLL_SECONDS", 15.0))

app = FastAPI(title="Throttle Agent")

_last_poll_ts: float = 0.0
_last_ram_pct: float | None = None


@app.on_event("startup")
def startup() -> None:
    if AUTO_THROTTLE_ENABLED:
        logger.info("AUTO_THROTTLE_ENABLED is true")
    else:
        logger.info("AUTO_THROTTLE_ENABLED is false")


@app.get("/health")
def health() -> dict[str, Any]:
    try:
        _docker_client().ping()
        DOCKER_UP.set(1)
        return {"status": "healthy", "agent": "throttle-agent", "docker": "ok"}
    except Exception as e:
        DOCKER_UP.set(0)
        return {"status": "degraded", "agent": "throttle-agent", "docker": "error", "detail": str(e)}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(PROM_REGISTRY), media_type=CONTENT_TYPE_LATEST)


@app.get("/tiers")
def tiers() -> dict[str, Any]:
    tiers_cfg = _get_tiers()
    try:
        client = _docker_client()
        client.ping()
        DOCKER_UP.set(1)
    except Exception as e:
        DOCKER_UP.set(0)
        return {"error": "docker_unreachable", "detail": str(e)}

    data: dict[int, TierStatus] = {}
    for tier, names in tiers_cfg.items():
        data[tier] = _get_tier_status(client, tier, names)
    return {"tiers": {k: v.model_dump() for k, v in data.items()}}


@app.get("/decisions")
def decisions() -> dict[str, Any]:
    global _last_poll_ts, _last_ram_pct

    tiers_cfg = _get_tiers()
    try:
        client = _docker_client()
        client.ping()
        DOCKER_UP.set(1)
    except Exception as e:
        DOCKER_UP.set(0)
        return {"error": "docker_unreachable", "detail": str(e)}

    now = time.time()
    if now - _last_poll_ts > POLL_SECONDS or _last_ram_pct is None:
        _last_poll_ts = now
        _last_ram_pct = _estimate_system_ram_pct(client, tiers_cfg)
        if _last_ram_pct is not None:
            SYSTEM_RAM_USAGE_PCT.set(_last_ram_pct)

    ram_pct = _last_ram_pct
    actions: list[str] = []
    if ram_pct is None:
        actions.append("UNKNOWN: cannot determine system RAM usage")
    elif ram_pct >= RAM_EMERGENCY_PCT:
        actions.append("EMERGENCY: pause tier 6, then tier 5, then tier 4")
    elif ram_pct >= RAM_HIGH_PCT:
        actions.append("HIGH: pause tier 6, then tier 5")
    elif ram_pct >= RAM_WARN_PCT:
        actions.append("WARN: consider pausing tier 6")
    else:
        actions.append("ALL GREEN")

    return {
        "auto_throttle_enabled": AUTO_THROTTLE_ENABLED,
        "ram_pct": ram_pct,
        "thresholds": {
            "warn": RAM_WARN_PCT,
            "high": RAM_HIGH_PCT,
            "emergency": RAM_EMERGENCY_PCT,
        },
        "actions": actions,
    }


@app.post("/throttle/{tier}")
def throttle_tier(tier: int, action: str = "pause") -> dict[str, Any]:
    tiers_cfg = _get_tiers()
    if tier not in tiers_cfg:
        return {"error": "invalid_tier", "tier": tier}

    if action not in {"pause", "resume"}:
        return {"error": "invalid_action", "action": action}

    try:
        client = _docker_client()
        client.ping()
        DOCKER_UP.set(1)
    except Exception as e:
        DOCKER_UP.set(0)
        return {"error": "docker_unreachable", "detail": str(e)}

    changed: list[str] = []
    failed: dict[str, str] = {}

    for name in tiers_cfg[tier]:
        if name == "throttle-agent":
            continue
        try:
            container = client.containers.get(name)
            if action == "pause":
                container.pause()
            else:
                container.unpause()
            THROTTLE_ACTIONS_TOTAL.labels(tier=str(tier), action=action, container=name).inc()
            changed.append(name)
            logger.info("%s %s (tier %s)", action, name, tier)
        except Exception as e:
            failed[name] = str(e)

    return {"tier": tier, "action": action, "changed": changed, "failed": failed}
