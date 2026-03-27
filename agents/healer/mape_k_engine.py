"""
🧠 MAPE-K ENGINE — HyperCode V2.0 Self-Healing Brain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAP-K Loop: Monitor → Analyze → Plan → Execute
Knowledge Base: PostgreSQL + in-memory cache

Phase 1: Reactive healing with Z-score anomaly detection
Phase 2: Predictive healing (Isolation Forest) — coming soon!

Built by @welshDog 🏴󠁧󠁢󠁷󠁬󠁳󠁿♾ — HyperFocus Zone, Llanelli, Wales
"""

import asyncio
import time
import statistics
import httpx
import logging
import docker as docker_sdk  # BUG FIX: removed duplicate import
from datetime import datetime, timezone
from collections import deque, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger("mape_k")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗺️ KNOWLEDGE BASE — Shared state
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ServiceStatus(str, Enum):  # BUG FIX: restored proper indentation
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealAction(str, Enum):  # BUG FIX: restored proper indentation
    HTTP_RESTART = "http_restart"   # POST /restart to agent
    DOCKER_RESTART = "docker_restart"  # docker SDK container restart
    SCALE_UP = "scale_up"           # future: k8s/compose scale
    ALERT_ONLY = "alert_only"       # log + notify, no action
    NO_ACTION = "no_action"


@dataclass
class ServiceConfig:  # BUG FIX: restored proper indentation
    name: str
    port: int
    check_url: str
    compose_name: Optional[str] = None
    restart_url: Optional[str] = None
    critical: bool = True
    history: deque = field(default_factory=lambda: deque(maxlen=60))
    last_status: ServiceStatus = ServiceStatus.UNKNOWN
    consecutive_failures: int = 0
    total_heals: int = 0
    last_healed: Optional[float] = None


@dataclass
class HealEvent:  # BUG FIX: restored proper indentation
    timestamp: str
    service: str
    status_before: ServiceStatus
    action_taken: HealAction
    success: bool
    reason: str
    mttr_seconds: Optional[float] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔭 KNOWLEDGE BASE SINGLETON
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class KnowledgeBase:
    """The K in MAPE-K. Shared memory across all phases."""

    def __init__(self):
        self.heal_history: list[HealEvent] = []
        self.anomaly_scores: dict[str, float] = {}
        self.action_success_rates: dict[HealAction, list[bool]] = defaultdict(list)
        self.system_start = time.time()

    def record_heal(self, event: HealEvent):
        self.heal_history.append(event)
        self.action_success_rates[event.action_taken].append(event.success)
        if len(self.heal_history) > 500:
            self.heal_history = self.heal_history[-500:]

    def success_rate(self, action: HealAction) -> float:
        results = self.action_success_rates.get(action, [])
        if not results:
            return 0.0
        return sum(results) / len(results)

    def recent_heals(self, minutes: int = 60) -> list[HealEvent]:
        cutoff = time.time() - (minutes * 60)
        cutoff_str = datetime.fromtimestamp(cutoff, tz=timezone.utc).isoformat()
        return [e for e in self.heal_history if e.timestamp >= cutoff_str]

    def stats(self) -> dict:
        recent = self.recent_heals(60)
        successful = [e for e in recent if e.success]
        mttr_values = [e.mttr_seconds for e in successful if e.mttr_seconds]
        return {
            "total_heals": len(self.heal_history),
            "heals_last_hour": len(recent),
            "auto_fix_success_rate": round(
                len(successful) / len(recent) * 100 if recent else 0, 1
            ),
            "avg_mttr_seconds": round(statistics.mean(mttr_values), 1) if mttr_values else None,
            "uptime_seconds": round(time.time() - self.system_start),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📡 MONITOR PHASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def monitor(service: ServiceConfig) -> tuple[ServiceStatus, float]:
    """Poll a service and return (status, response_time_ms)."""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(service.check_url)
        elapsed = (time.monotonic() - start) * 1000
        if resp.status_code < 500:
            status = ServiceStatus.HEALTHY
        else:
            status = ServiceStatus.DEGRADED
    except Exception:
        elapsed = (time.monotonic() - start) * 1000
        status = ServiceStatus.CRITICAL

    service.history.append((time.time(), status, elapsed))
    return status, elapsed


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔬 ANALYZE PHASE — Z-Score Anomaly Detection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze(
    service: ServiceConfig,
    current_status: ServiceStatus,
    response_ms: float,
    kb: KnowledgeBase,
) -> tuple[bool, str, float]:
    """
    Returns (is_anomaly, reason, anomaly_score).
    Uses Z-score on response time + consecutive failure counting.
    Z-score > 3.0 = anomaly (industry standard 3-sigma rule)
    """
    # --- Response time Z-score ---
    response_times = [
        rt for _, _, rt in service.history
        if rt is not None and rt > 0
    ]
    z_score = 0.0
    if len(response_times) >= 10:
        mean_rt = statistics.mean(response_times)
        stdev_rt = statistics.stdev(response_times)
        if stdev_rt > 0:
            z_score = abs((response_ms - mean_rt) / stdev_rt)

    kb.anomaly_scores[service.name] = round(z_score, 2)

    # --- Consecutive failures ---
    if current_status == ServiceStatus.CRITICAL:
        service.consecutive_failures += 1
    else:
        service.consecutive_failures = 0

    # --- Decision logic ---
    if current_status == ServiceStatus.CRITICAL and service.consecutive_failures >= 2:
        return True, f"CRITICAL: {service.consecutive_failures} consecutive failures", z_score

    if current_status == ServiceStatus.DEGRADED and service.consecutive_failures >= 3:
        return True, f"DEGRADED: {service.consecutive_failures} consecutive slow responses", z_score

    if z_score > 3.0 and current_status != ServiceStatus.HEALTHY:
        return True, f"ANOMALY: Z-score={z_score:.1f} (threshold=3.0)", z_score

    return False, "nominal", z_score


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 PLAN PHASE — Action Priority Queue
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def plan(
    service: ServiceConfig,
    status: ServiceStatus,
    reason: str,
    kb: KnowledgeBase,
) -> HealAction:
    """
    Choose the best heal action based on:
    - Service criticality
    - Available endpoints
    - Historical success rates
    Priority: soft restart → docker restart → alert
    """
    # Cooldown: don't spam restarts (60s minimum between heals)
    if service.last_healed and (time.time() - service.last_healed) < 60:
        logger.info(f"[PLAN] {service.name} — cooldown active, skipping heal")
        return HealAction.NO_ACTION

    # Non-critical services: alert only
    if not service.critical:
        return HealAction.ALERT_ONLY

    # Prefer soft HTTP restart if available and historically effective
    if service.restart_url:
        soft_rate = kb.success_rate(HealAction.HTTP_RESTART)
        if soft_rate >= 0.5 or not kb.action_success_rates[HealAction.HTTP_RESTART]:
            return HealAction.HTTP_RESTART

    # Fall back to docker restart
    if service.compose_name:
        return HealAction.DOCKER_RESTART

    return HealAction.ALERT_ONLY


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ EXECUTE PHASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def execute(
    service: ServiceConfig,
    action: HealAction,
    reason: str,
    kb: KnowledgeBase,
) -> HealEvent:
    """Apply the healing action and record the result."""
    started_at = time.time()
    success = False
    ts = datetime.now(tz=timezone.utc).isoformat()

    logger.warning(f"[EXECUTE] 🩺 Healing {service.name} via {action.value} — {reason}")

    if action == HealAction.HTTP_RESTART and service.restart_url:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(service.restart_url)
            success = resp.status_code < 400
        except Exception as e:
            logger.error(f"[EXECUTE] HTTP restart failed: {e}")

    elif action == HealAction.DOCKER_RESTART and service.compose_name:
        try:
            # BUG FIX: docker SDK is sync — must run in thread to avoid blocking async event loop
            def _docker_restart():
                client = docker_sdk.from_env()
                container = client.containers.get(service.compose_name)
                container.restart()

            await asyncio.to_thread(_docker_restart)
            success = True
            logger.info(f"[EXECUTE] ✅ Docker SDK restart sent to {service.compose_name}")
        except docker_sdk.errors.NotFound:
            logger.error(f"[EXECUTE] Container {service.compose_name} not found")
        except Exception as e:
            logger.error(f"[EXECUTE] Docker restart failed: {e}")

    elif action == HealAction.ALERT_ONLY:
        success = True
        logger.warning(f"[ALERT] {service.name} degraded — {reason}")

    elif action == HealAction.NO_ACTION:
        success = True

    # Calculate MTTR if heal was attempted
    mttr = None
    if success and action not in (HealAction.NO_ACTION, HealAction.ALERT_ONLY):
        await asyncio.sleep(5)
        post_status, _ = await monitor(service)
        if post_status == ServiceStatus.HEALTHY:
            mttr = round(time.time() - started_at, 1)
            logger.info(f"[EXECUTE] ✅ {service.name} recovered in {mttr}s")
        else:
            success = False
            logger.warning(f"[EXECUTE] ⚠️ {service.name} still unhealthy after heal attempt")

    service.total_heals += 1
    service.last_healed = time.time()

    event = HealEvent(
        timestamp=ts,
        service=service.name,
        status_before=service.last_status,
        action_taken=action,
        success=success,
        reason=reason,
        mttr_seconds=mttr,
    )
    kb.record_heal(event)
    return event


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔄 MAPE-K MAIN LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def mape_k_loop(
    services: list[ServiceConfig],
    kb: KnowledgeBase,
    interval_seconds: int = 10,
):
    """The core MAPE-K loop — runs forever, heals everything."""
    logger.info("🧠 MAPE-K Engine ONLINE — HyperCode self-healing active!")

    while True:
        cycle_start = time.time()

        for service in services:
            try:
                # 📡 MONITOR
                status, response_ms = await monitor(service)

                # 🔬 ANALYZE
                is_anomaly, reason, z_score = analyze(service, status, response_ms, kb)

                service.last_status = status

                if is_anomaly:
                    logger.warning(
                        f"[ANALYZE] ⚠️ {service.name} anomaly detected! "
                        f"status={status.value} z={z_score:.1f} — {reason}"
                    )

                    # 📋 PLAN
                    action = plan(service, status, reason, kb)

                    # ⚡ EXECUTE
                    if action != HealAction.NO_ACTION:
                        await execute(service, action, reason, kb)

            except Exception as e:
                logger.error(f"[MAPE-K] Error processing {service.name}: {e}")

        cycle_time = time.time() - cycle_start
        sleep_time = max(0, interval_seconds - cycle_time)
        await asyncio.sleep(sleep_time)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ DEFAULT SERVICE REGISTRY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NOTE: URLs use Docker internal container hostnames (backend-net),
# NOT localhost — the healer runs inside a container.

DEFAULT_SERVICES = [
    ServiceConfig("HyperCode Backend",    8000,  "http://hypercode-core:8000/health",         "hypercode-core"),
    ServiceConfig("Healer Agent",         8008,  "http://healer-agent:8008/health",           "healer-agent",         critical=False),
    ServiceConfig("Crew Orchestrator",    8080,  "http://crew-orchestrator:8080/health",      "crew-orchestrator"),
    ServiceConfig("Super BROski Agent",   8015,  "http://super-hyper-broski:8015/health",     "super-hyper-broski"),
    ServiceConfig("Throttle Agent",       8014,  "http://throttle-agent:8014/health",         "throttle-agent"),
    ServiceConfig("Test Agent",           8013,  "http://test-agent:8013/health",             "test-agent"),
    ServiceConfig("Tips Writer",          8011,  "http://tips-tricks-writer:8011/health",     "tips-tricks-writer"),
    ServiceConfig("Mission Control",      8088,  "http://hypercode-dashboard:8088/health",    "hypercode-dashboard"),
    ServiceConfig("MCP Gateway",          8820,  "http://mcp-gateway:8820/health",            "mcp-gateway"),
    ServiceConfig("MCP REST Adapter",     8821,  "http://mcp-rest-adapter:8821/health",       "mcp-rest-adapter"),
    ServiceConfig("Ollama LLM",           11434, "http://hypercode-ollama:11434/api/tags",    "hypercode-ollama"),
    ServiceConfig("Prometheus",           9090,  "http://prometheus:9090/-/healthy",          "prometheus",           critical=False),
    ServiceConfig("Grafana",              3001,  "http://grafana:3001/api/health",            "grafana",              critical=False),
    ServiceConfig("HyperHealth API",      8090,  "http://hyperhealth-api:8090/health",        "hyperhealth-api",      critical=False),
]
