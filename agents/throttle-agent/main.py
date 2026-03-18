"""throttle-agent FastAPI service."""

from __future__ import annotations

import logging
import asyncio
import os
import time
from typing import Any

import docker
from docker.errors import DockerException, NotFound
from fastapi import FastAPI, Response
import httpx
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

TIER_PAUSED = Gauge(
    "throttle_tier_paused",
    "Whether a tier is currently paused by Throttle (1/0)",
    ["tier"],
    registry=PROM_REGISTRY,
)
CONTAINER_PAUSED_BY_THROTTLE = Gauge(
    "throttle_container_paused_by_throttle",
    "Whether a container is marked as paused by Throttle (1/0)",
    ["container_name"],
    registry=PROM_REGISTRY,
)
HEALER_CIRCUIT_OPEN = Gauge(
    "throttle_healer_circuit_open",
    "Whether Healer circuit breaker is open for a service (1/0)",
    ["service_name"],
    registry=PROM_REGISTRY,
)
RAM_THRESHOLD_PCT = Gauge(
    "throttle_ram_threshold_pct",
    "Current configured RAM thresholds used by Throttle",
    ["level"],
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

ALL_CONTAINERS: list[str] = sorted({c for tier in DEFAULT_TIERS.values() for c in tier})


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


HEALER_URL = os.getenv("HEALER_URL", "http://healer-agent:8008").strip() or "http://healer-agent:8008"

AUTO_THROTTLE_ENABLED = os.getenv("AUTO_THROTTLE_ENABLED", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

THROTTLE_PAUSE_TIER6_AT = _parse_threshold("THROTTLE_PAUSE_TIER6_AT", 80.0)
THROTTLE_PAUSE_TIER5_AT = _parse_threshold("THROTTLE_PAUSE_TIER5_AT", 90.0)
THROTTLE_PAUSE_TIER4_AT = _parse_threshold("THROTTLE_PAUSE_TIER4_AT", 95.0)
THROTTLE_RESUME_BELOW = _parse_threshold("THROTTLE_RESUME_BELOW", 75.0)
THROTTLE_RESUME_HOLD_MINUTES = int(_parse_threshold("THROTTLE_RESUME_HOLD_MINUTES", 5.0))
THROTTLE_PAUSE_TTL_SECONDS = int(_parse_threshold("THROTTLE_PAUSE_TTL_SECONDS", 900.0))
THROTTLE_KEEP_OBSERVABILITY = os.getenv("THROTTLE_KEEP_OBSERVABILITY", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
POLL_INTERVAL_SECONDS = int(_parse_threshold("POLL_INTERVAL_SECONDS", 30.0))


def _parse_int_set(raw: str) -> set[int]:
    out: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.add(int(part))
        except ValueError:
            continue
    return out


def _parse_str_set(raw: str) -> set[str]:
    return {p.strip() for p in raw.split(",") if p.strip()}


THROTTLE_PROTECT_TIERS = _parse_int_set(os.getenv("THROTTLE_PROTECT_TIERS", "1,2,3"))
THROTTLE_PROTECT_CONTAINERS = _parse_str_set(
    os.getenv("THROTTLE_PROTECT_CONTAINERS", "throttle-agent,healer-agent,hypercode-core,postgres,redis")
)
THROTTLE_ACTIVE_CONTAINER = os.getenv("THROTTLE_ACTIVE_CONTAINER", "").strip()
if THROTTLE_ACTIVE_CONTAINER:
    THROTTLE_PROTECT_CONTAINERS.add(THROTTLE_ACTIVE_CONTAINER)

app = FastAPI(title="Throttle Agent")

_last_poll_ts: float = 0.0
_last_ram_pct: float | None = None
_autopilot_below_since: float | None = None
_autopilot_paused_tiers: set[int] = set()
_last_healer_state_poll_ts: float = 0.0
_last_paused_by_throttle: set[str] = set()
_last_open_circuits: set[str] = set()


def _fetch_healer_paused_by_throttle() -> set[str]:
    try:
        r = httpx.get(f"{HEALER_URL}/throttle/state", timeout=2.0)
        if r.status_code != 200:
            return set()
        data = r.json()
        containers = data.get("containers", [])
        if not isinstance(containers, list):
            return set()
        return {c for c in containers if isinstance(c, str) and c}
    except Exception:
        return set()


def _fetch_healer_open_circuits() -> set[str]:
    try:
        r = httpx.get(f"{HEALER_URL}/circuit-breaker/status", timeout=2.0)
        if r.status_code != 200:
            return set()
        data = r.json()
        open_circuits = data.get("open_circuits", [])
        if not isinstance(open_circuits, list):
            return set()
        return {c for c in open_circuits if isinstance(c, str) and c}
    except Exception:
        return set()


def _update_grafana_metrics() -> None:
    global _last_healer_state_poll_ts, _last_paused_by_throttle, _last_open_circuits

    RAM_THRESHOLD_PCT.labels(level="pause_tier6_at").set(THROTTLE_PAUSE_TIER6_AT)
    RAM_THRESHOLD_PCT.labels(level="pause_tier5_at").set(THROTTLE_PAUSE_TIER5_AT)
    RAM_THRESHOLD_PCT.labels(level="pause_tier4_at").set(THROTTLE_PAUSE_TIER4_AT)
    RAM_THRESHOLD_PCT.labels(level="resume_below").set(THROTTLE_RESUME_BELOW)

    now = time.time()
    if now - _last_healer_state_poll_ts >= 10:
        _last_healer_state_poll_ts = now
        _last_paused_by_throttle = _fetch_healer_paused_by_throttle()
        _last_open_circuits = _fetch_healer_open_circuits()

    paused = _last_paused_by_throttle
    for c in ALL_CONTAINERS:
        CONTAINER_PAUSED_BY_THROTTLE.labels(container_name=c).set(1 if c in paused else 0)

    for tier, containers in _get_tiers().items():
        tier_paused = any(c in paused for c in containers)
        TIER_PAUSED.labels(tier=str(tier)).set(1 if tier_paused else 0)

    open_circuits = _last_open_circuits
    for c in ALL_CONTAINERS:
        HEALER_CIRCUIT_OPEN.labels(service_name=c).set(1 if c in open_circuits else 0)


def _notify_healer_state(containers: list[str], paused: bool) -> None:
    if not containers:
        return
    payload = {
        "containers": containers,
        "paused": paused,
        "ttl_seconds": THROTTLE_PAUSE_TTL_SECONDS,
        "reason": "throttle_agent",
    }
    try:
        httpx.post(f"{HEALER_URL}/throttle/state", json=payload, timeout=2.0)
    except Exception:
        return


def _healer_allows_resume(container: str) -> bool:
    try:
        r = httpx.get(f"{HEALER_URL}/circuit-breaker/{container}", timeout=2.0)
        if r.status_code != 200:
            return True
        data = r.json()
        return data.get("state") != "open"
    except Exception:
        return True


def _tier_container_names(tier: int) -> list[str]:
    tiers = _get_tiers()
    return list(tiers.get(tier, []))


def _pause_tier_sync(client: docker.DockerClient, tier: int) -> dict[str, Any]:
    changed: list[str] = []
    failed: dict[str, str] = {}
    targets = _tier_container_names(tier)
    for name in targets:
        if name in THROTTLE_PROTECT_CONTAINERS:
            continue
        try:
            container = client.containers.get(name)
            container.pause()
            THROTTLE_ACTIONS_TOTAL.labels(tier=str(tier), action="pause", container=name).inc()
            changed.append(name)
        except Exception as e:
            failed[name] = str(e)
    if changed:
        _notify_healer_state(changed, paused=True)
    return {"tier": tier, "action": "pause", "changed": changed, "failed": failed}


def _resume_tier_sync(client: docker.DockerClient, tier: int) -> dict[str, Any]:
    changed: list[str] = []
    failed: dict[str, str] = {}
    skipped: list[str] = []
    targets = _tier_container_names(tier)
    for name in targets:
        if name in THROTTLE_PROTECT_CONTAINERS:
            continue
        if not _healer_allows_resume(name):
            skipped.append(name)
            continue
        try:
            container = client.containers.get(name)
            container.unpause()
            THROTTLE_ACTIONS_TOTAL.labels(tier=str(tier), action="resume", container=name).inc()
            changed.append(name)
        except Exception as e:
            failed[name] = str(e)
    if changed:
        _notify_healer_state(changed, paused=False)
    return {"tier": tier, "action": "resume", "changed": changed, "skipped": skipped, "failed": failed}


def _autopilot_cycle_sync() -> None:
    global _autopilot_below_since, _autopilot_paused_tiers, _last_poll_ts, _last_ram_pct

    tiers_cfg = _get_tiers()
    client = _docker_client()
    client.ping()
    DOCKER_UP.set(1)

    _last_poll_ts = time.time()
    _last_ram_pct = _estimate_system_ram_pct(client, tiers_cfg)
    if _last_ram_pct is not None:
        SYSTEM_RAM_USAGE_PCT.set(_last_ram_pct)

    _update_grafana_metrics()

    ram_pct = _last_ram_pct
    if ram_pct is None:
        return

    desired_pause: list[int] = []
    if ram_pct >= THROTTLE_PAUSE_TIER4_AT:
        desired_pause = [6, 5, 4]
    elif ram_pct >= THROTTLE_PAUSE_TIER5_AT:
        desired_pause = [6, 5]
    elif ram_pct >= THROTTLE_PAUSE_TIER6_AT:
        desired_pause = [6]

    if THROTTLE_KEEP_OBSERVABILITY and ram_pct < THROTTLE_PAUSE_TIER5_AT:
        desired_pause = [t for t in desired_pause if t != 5]

    for tier in desired_pause:
        if tier in THROTTLE_PROTECT_TIERS:
            continue
        if tier in _autopilot_paused_tiers:
            continue
        _pause_tier_sync(client, tier)
        _autopilot_paused_tiers.add(tier)

    if ram_pct < THROTTLE_RESUME_BELOW:
        if _autopilot_below_since is None:
            _autopilot_below_since = time.time()
    else:
        _autopilot_below_since = None

    if _autopilot_paused_tiers and _autopilot_below_since is not None:
        hold_seconds = max(THROTTLE_RESUME_HOLD_MINUTES, 1) * 60
        if time.time() - _autopilot_below_since >= hold_seconds:
            for tier in [4, 5, 6]:
                if tier in _autopilot_paused_tiers:
                    _resume_tier_sync(client, tier)
                    _autopilot_paused_tiers.remove(tier)
            if not _autopilot_paused_tiers:
                _autopilot_below_since = None


@app.on_event("startup")
async def startup() -> None:
    if AUTO_THROTTLE_ENABLED:
        logger.info("AUTO_THROTTLE_ENABLED is true")
        asyncio.create_task(_autopilot_loop())
    else:
        logger.info("AUTO_THROTTLE_ENABLED is false")


async def _autopilot_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(_autopilot_cycle_sync)
        except Exception as e:
            logger.error("Autopilot error: %s", e)
        await asyncio.sleep(max(POLL_INTERVAL_SECONDS, 5))


@app.get("/health")
def health() -> dict[str, Any]:
    healer_ok: bool | None = None
    try:
        r = httpx.get(f"{HEALER_URL}/health", timeout=2.0)
        healer_ok = r.status_code == 200
    except Exception:
        healer_ok = None
    try:
        _docker_client().ping()
        DOCKER_UP.set(1)
        return {
            "status": "healthy",
            "agent": "throttle-agent",
            "docker": "ok",
            "healer_ok": healer_ok,
        }
    except Exception as e:
        DOCKER_UP.set(0)
        return {
            "status": "degraded",
            "agent": "throttle-agent",
            "docker": "error",
            "detail": str(e),
            "healer_ok": healer_ok,
        }


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
    _update_grafana_metrics()
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
    if now - _last_poll_ts > POLL_INTERVAL_SECONDS or _last_ram_pct is None:
        _last_poll_ts = now
        _last_ram_pct = _estimate_system_ram_pct(client, tiers_cfg)
        if _last_ram_pct is not None:
            SYSTEM_RAM_USAGE_PCT.set(_last_ram_pct)

    _update_grafana_metrics()

    ram_pct = _last_ram_pct
    actions: list[str] = []
    if ram_pct is None:
        actions.append("UNKNOWN: cannot determine system RAM usage")
    elif ram_pct >= THROTTLE_PAUSE_TIER4_AT:
        actions.append("EMERGENCY: pause tier 6, then tier 5, then tier 4")
    elif ram_pct >= THROTTLE_PAUSE_TIER5_AT:
        actions.append("HIGH: pause tier 6, then tier 5")
    elif ram_pct >= THROTTLE_PAUSE_TIER6_AT:
        actions.append("WARN: consider pausing tier 6")
    else:
        actions.append("ALL GREEN")

    return {
        "auto_throttle_enabled": AUTO_THROTTLE_ENABLED,
        "ram_pct": ram_pct,
        "thresholds": {
            "pause_tier6_at": THROTTLE_PAUSE_TIER6_AT,
            "pause_tier5_at": THROTTLE_PAUSE_TIER5_AT,
            "pause_tier4_at": THROTTLE_PAUSE_TIER4_AT,
            "resume_below": THROTTLE_RESUME_BELOW,
            "resume_hold_minutes": THROTTLE_RESUME_HOLD_MINUTES,
        },
        "protect": {
            "tiers": sorted(THROTTLE_PROTECT_TIERS),
            "containers": sorted(THROTTLE_PROTECT_CONTAINERS),
            "active_container": THROTTLE_ACTIVE_CONTAINER or None,
            "keep_observability": THROTTLE_KEEP_OBSERVABILITY,
        },
        "autopilot": {
            "paused_tiers": sorted(_autopilot_paused_tiers),
            "poll_interval_seconds": POLL_INTERVAL_SECONDS,
        },
        "healer_url": HEALER_URL,
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

    if action == "pause":
        return _pause_tier_sync(client, tier)
    return _resume_tier_sync(client, tier)
