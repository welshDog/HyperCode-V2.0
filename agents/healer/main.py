from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import Any, Dict, List, Optional
import asyncio
import httpx
import os
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse
import redis.asyncio as redis
from collections import defaultdict
import time
from healer.adapters.docker_adapter import DockerAdapter
from healer.models import HealRequest, HealResult
from pydantic import BaseModel

# Setup logging with JSON format for production
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("healer.main")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://crew-orchestrator:8080")
WATCHDOG_ENABLED = os.getenv("HEALER_WATCHDOG_ENABLED", "false").strip().lower() == "true"
WATCHDOG_INTERVAL_SECONDS = float(os.getenv("HEALER_WATCHDOG_INTERVAL_SECONDS", "60").strip() or "60")
WATCHDOG_SMOKE_API_KEY = os.getenv("HEALER_SMOKE_API_KEY", "").strip()
WATCHDOG_ORCHESTRATOR_API_KEY = os.getenv("HEALER_ORCHESTRATOR_API_KEY", "").strip()
WATCHDOG_AGENT = os.getenv("HEALER_WATCHDOG_AGENT", "").strip()
WATCHDOG_FORCE_RESTART = os.getenv("HEALER_WATCHDOG_FORCE_RESTART", "false").strip().lower() == "true"

redis_client: Optional[redis.Redis] = None
docker_adapter: Optional[DockerAdapter] = None
_throttle_paused_local: Dict[str, float] = {}


class ThrottleStateUpdate(BaseModel):
    containers: List[str]
    paused: bool = True
    ttl_seconds: int = 900
    reason: Optional[str] = None


def _throttle_pause_key(container: str) -> str:
    return f"throttle:paused:{container}"


async def set_throttle_state(update: ThrottleStateUpdate) -> Dict[str, Any]:
    now = time.time()
    ttl = max(int(update.ttl_seconds), 10)
    applied: List[str] = []

    if redis_client:
        if update.paused:
            payload = json.dumps(
                {
                    "paused": True,
                    "reason": update.reason,
                    "until_ts": now + ttl,
                }
            )
            for c in update.containers:
                if not isinstance(c, str) or not c:
                    continue
                await redis_client.set(_throttle_pause_key(c), payload, ex=ttl)
                applied.append(c)
        else:
            keys = [_throttle_pause_key(c) for c in update.containers if isinstance(c, str) and c]
            if keys:
                await redis_client.delete(*keys)
                applied = [c for c in update.containers if isinstance(c, str) and c]
    else:
        if update.paused:
            until = now + ttl
            for c in update.containers:
                if not isinstance(c, str) or not c:
                    continue
                _throttle_paused_local[c] = until
                applied.append(c)
        else:
            for c in update.containers:
                if not isinstance(c, str) or not c:
                    continue
                _throttle_paused_local.pop(c, None)
                applied.append(c)

    return {"applied": applied, "paused": update.paused, "ttl_seconds": ttl}


async def is_throttle_paused(container: str) -> bool:
    if redis_client:
        value = await redis_client.get(_throttle_pause_key(container))
        return value is not None
    until = _throttle_paused_local.get(container)
    if until is None:
        return False
    if time.time() > until:
        _throttle_paused_local.pop(container, None)
        return False
    return True


async def get_throttle_state() -> Dict[str, Any]:
    if redis_client:
        keys = await redis_client.keys("throttle:paused:*")
        containers = [k.split("throttle:paused:", 1)[1] for k in keys if isinstance(k, str) and k.startswith("throttle:paused:")]
        return {"containers": sorted(set(containers)), "backend": "redis"}
    now = time.time()
    containers = [c for c, until in _throttle_paused_local.items() if until > now]
    return {"containers": sorted(set(containers)), "backend": "memory"}


# Circuit Breaker Pattern - Prevents infinite retry loops
class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=60):
        self.failure_counts = defaultdict(int)
        self.last_failure_time = {}
        self.failure_threshold = failure_threshold
        self.timeout = timeout
    
    def is_open(self, agent_name: str) -> bool:
        """Check if circuit is open (too many failures)"""
        if agent_name not in self.last_failure_time:
            return False
        
        # Reset after timeout
        if datetime.now() - self.last_failure_time[agent_name] > timedelta(seconds=self.timeout):
            self.failure_counts[agent_name] = 0
            return False
        
        return self.failure_counts[agent_name] >= self.failure_threshold
    
    def record_failure(self, agent_name: str):
        self.failure_counts[agent_name] += 1
        self.last_failure_time[agent_name] = datetime.now()
        logger.warning(f"Circuit breaker: {agent_name} failures = {self.failure_counts[agent_name]}/{self.failure_threshold}")
    
    def record_success(self, agent_name: str):
        if self.failure_counts[agent_name] > 0:
            logger.info(f"Circuit breaker: {agent_name} recovered - resetting failure count")
        self.failure_counts[agent_name] = 0
        if agent_name in self.last_failure_time:
            del self.last_failure_time[agent_name]


circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, docker_adapter
    # Startup
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    docker_adapter = DockerAdapter(redis_url=REDIS_URL)
    
    # Subscribe to orchestrator alerts
    asyncio.create_task(alert_listener())
    if WATCHDOG_ENABLED:
        asyncio.create_task(watchdog_loop())
    
    logger.info("Healer Agent started - monitoring system health")
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()
    logger.info("Healer Agent shutting down")


app = FastAPI(
    title="Healer Agent", 
    version="0.2.0", 
    description="Autonomous healing service for agents and systems",
    lifespan=lifespan
)


async def fetch_system_health() -> Dict[str, Dict]:
    """Fetch health status of all system components"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{ORCHESTRATOR_URL}/system/health")
            if r.status_code != 200:
                logger.error(f"Failed to fetch system health: {r.status_code}")
                return {}
            return r.json()
    except Exception as e:
        logger.error(f"Error fetching system health: {e}")
        return {}


async def fetch_agent_roster() -> Dict[str, str]:
    try:
        headers = {"Content-Type": "application/json"}
        if WATCHDOG_ORCHESTRATOR_API_KEY:
            headers["X-API-Key"] = WATCHDOG_ORCHESTRATOR_API_KEY
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{ORCHESTRATOR_URL}/agents", headers=headers)
            if r.status_code != 200:
                return {}
            data = r.json()
            if not isinstance(data, list):
                return {}
            roster: Dict[str, str] = {}
            for item in data:
                if not isinstance(item, dict):
                    continue
                agent_id = item.get("id")
                url = item.get("url")
                if isinstance(agent_id, str) and isinstance(url, str) and agent_id and url:
                    roster[agent_id] = url
            return roster
    except Exception:
        return {}


async def watchdog_cycle() -> None:
    if not WATCHDOG_SMOKE_API_KEY:
        return

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": WATCHDOG_SMOKE_API_KEY,
        "X-Smoke-Mode": "true",
    }

    roster = await fetch_agent_roster()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {"mode": "probe_health"}
            if WATCHDOG_AGENT:
                payload["agent"] = WATCHDOG_AGENT
            r = await client.post(
                f"{ORCHESTRATOR_URL}/execute/smoke",
                headers=headers,
                json=payload,
            )
    except Exception:
        return

    if r.status_code != 200:
        return

    try:
        payload = r.json()
    except Exception:
        return

    agents = payload.get("agents")
    if not isinstance(agents, dict):
        return

    heal_tasks = []
    for agent_id, result in agents.items():
        if not isinstance(agent_id, str) or not isinstance(result, dict):
            continue
        status = result.get("status")
        if status not in {"unhealthy", "down"}:
            continue
        agent_url = roster.get(agent_id)
        if not agent_url:
            continue
        parsed = urlparse(agent_url)
        container_name = parsed.hostname or agent_id.replace("_", "-")
        logger.warning(f"Watchdog detected {agent_id}={status} -> healing {container_name}")
        heal_tasks.append(
            attempt_heal_agent(
                container_name,
                agent_url,
                attempts=2,
                timeout=5.0,
                force_restart=WATCHDOG_FORCE_RESTART,
            )
        )

    if not heal_tasks:
        return

    try:
        await asyncio.wait_for(asyncio.gather(*heal_tasks, return_exceptions=True), timeout=120.0)
    except Exception:
        return


async def watchdog_loop() -> None:
    if not WATCHDOG_SMOKE_API_KEY:
        logger.warning("Watchdog enabled but HEALER_SMOKE_API_KEY is not set")
    while True:
        try:
            await watchdog_cycle()
        except Exception:
            pass
        await asyncio.sleep(max(WATCHDOG_INTERVAL_SECONDS, 5.0))


async def ping_agent_health(agent_url: str, timeout: float) -> bool:
    """Check if an agent responds to health check"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(f"{agent_url}/health")
            return r.status_code == 200
    except Exception as e:
        logger.debug(f"Health check failed for {agent_url}: {e}")
        return False


async def attempt_heal_agent(
    agent_name: str, 
    agent_url: str, 
    attempts: int, 
    timeout: float,
    force_restart: bool = False,
) -> HealResult:
    """
    Attempt to heal an unhealthy agent with improved timeout handling.
    
    Uses exponential backoff and circuit breaker pattern to prevent
    resource exhaustion from repeatedly healing broken agents.
    """
    
    # Check circuit breaker first
    if circuit_breaker.is_open(agent_name):
        logger.warning(f"Circuit breaker OPEN for {agent_name} - skipping heal attempt")
        return HealResult(
            agent=agent_name,
            status="circuit_open",
            action="none",
            details="Too many consecutive failures - circuit breaker active (will retry in 60s)",
            timestamp=datetime.now().isoformat()
        )

    if await is_throttle_paused(agent_name):
        return HealResult(
            agent=agent_name,
            status="paused_by_throttle",
            action="none",
            details="Throttle Agent marked this container as intentionally paused",
            timestamp=datetime.now().isoformat(),
        )
    
    # Phase 1: Check if truly unhealthy
    logger.info(f"Checking health of {agent_name}...")
    healthy = await ping_agent_health(agent_url, timeout)
    if healthy:
        circuit_breaker.record_success(agent_name)
        return HealResult(
            agent=agent_name, 
            status="healthy", 
            action="none", 
            details="No action required", 
            timestamp=datetime.now().isoformat()
        )

    # Phase 2: Restart via Docker Adapter
    logger.warning(f"Agent {agent_name} is unhealthy. Attempting Docker restart...")
    
    if not docker_adapter:
        logger.error("Docker adapter not initialized")
        circuit_breaker.record_failure(agent_name)
        return HealResult(
            agent=agent_name, 
            status="failed", 
            action="restart", 
            details="Docker adapter unavailable", 
            timestamp=datetime.now().isoformat()
        )
    
    restarted = await docker_adapter.restart_container(agent_name, force=force_restart)
    if not restarted:
        logger.error(f"Docker restart failed for {agent_name}")
        circuit_breaker.record_failure(agent_name)
        return HealResult(
            agent=agent_name, 
            status="failed", 
            action="restart", 
            details="Docker restart command failed", 
            timestamp=datetime.now().isoformat()
        )
    
    # Phase 3: Wait for recovery with exponential backoff
    wait_times = [2, 5, 10]  # Try after 2s, 5s, 10s
    
    for wait_time in wait_times:
        await asyncio.sleep(wait_time)
        
        try:
            # Add timeout to prevent hanging
            is_healthy = await asyncio.wait_for(
                ping_agent_health(agent_url, timeout), 
                timeout=5.0
            )
            
            if is_healthy:
                logger.info(f"✅ Agent {agent_name} recovered after {wait_time}s")
                circuit_breaker.record_success(agent_name)
                return HealResult(
                    agent=agent_name, 
                    status="recovered", 
                    action="restart", 
                    details=f"Restart successful - recovered after {wait_time}s", 
                    timestamp=datetime.now().isoformat()
                )
        except asyncio.TimeoutError:
            logger.warning(f"Agent {agent_name} still unresponsive after {wait_time}s")
            continue
        except Exception as e:
            logger.error(f"Error checking {agent_name} health: {e}")
            continue
    
    # Failed all attempts
    logger.error(f"❌ Agent {agent_name} failed to recover after restart + 17s wait")
    circuit_breaker.record_failure(agent_name)
    return HealResult(
        agent=agent_name, 
        status="failed", 
        action="restart", 
        details="Agent unresponsive after restart and multiple health checks", 
        timestamp=datetime.now().isoformat()
    )


async def auto_heal_all():
    """
    Heal all unhealthy agents in parallel.
    
    Uses asyncio.gather for concurrent healing to minimize total recovery time.
    Includes global timeout to prevent infinite healing loops.
    """
    logger.info("🔧 Auto-healing triggered by system alert")
    health_data = await fetch_system_health()
    
    if not health_data:
        logger.warning("No health data available - skipping healing cycle")
        return
    
    # Build list of agents that need healing
    tasks = []
    for name, info in health_data.items():
        if info.get("status") == "unhealthy":
            url = info.get("url", f"http://{name}:8000")
            logger.info(f"Queuing healing task for {name}")
            tasks.append(attempt_heal_agent(name, url, attempts=2, timeout=5.0))
    
    if not tasks:
        logger.info("✅ All agents healthy - no healing needed")
        return
    
    # Heal all agents in parallel with global timeout
    try:
        logger.info(f"Healing {len(tasks)} agents in parallel...")
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=60.0  # Max 60 seconds for entire healing cycle
        )
        
        # Log results
        success_count = 0
        failure_count = 0
        
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Healing task raised exception: {res}")
                failure_count += 1
            elif res.status == "recovered" or res.status == "healthy":
                logger.info(f"✅ {res.agent}: {res.status} - {res.details}")
                success_count += 1
            else:
                logger.warning(f"❌ {res.agent}: {res.status} - {res.details}")
                failure_count += 1
        
        logger.info(f"Healing cycle complete: {success_count} succeeded, {failure_count} failed")
        
    except asyncio.TimeoutError:
        logger.error("⏱️ Auto-heal cycle exceeded 60s timeout - some agents may still be down")


@app.get("/health")
async def health():
    """Health check endpoint for the Healer Agent itself"""
    docker_ok = False
    if docker_adapter and docker_adapter.client:
        try:
            docker_adapter.client.ping()
            docker_ok = True
        except:
            pass
    
    redis_ok = redis_client is not None
    
    status = "healthy" if (docker_ok and redis_ok) else "degraded"
    
    return {
        "status": status,
        "healer": "online",
        "redis": redis_ok,
        "docker": docker_ok,
        "circuit_breaker_active": len(circuit_breaker.failure_counts) > 0,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health/sweep")
async def health_sweep():
    """
    Checks the health of all containers managed by Docker Adapter.
    Returns detailed report of all container statuses.
    """
    if not docker_adapter:
        raise HTTPException(status_code=503, detail="Docker adapter not initialized")
    
    try:
        report = await docker_adapter.check_all_containers()
        return report
    except Exception as e:
        logger.error(f"Health sweep failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/circuit-breaker/status")
async def circuit_breaker_status():
    """Get current circuit breaker state for all agents"""
    return {
        "failure_counts": dict(circuit_breaker.failure_counts),
        "open_circuits": [
            agent for agent in circuit_breaker.failure_counts.keys()
            if circuit_breaker.is_open(agent)
        ],
        "threshold": circuit_breaker.failure_threshold,
        "timeout_seconds": circuit_breaker.timeout
    }


@app.get("/circuit-breaker/{agent_name}")
async def circuit_breaker_agent_status(agent_name: str):
    count = int(circuit_breaker.failure_counts.get(agent_name, 0))
    is_open = circuit_breaker.is_open(agent_name)
    return {
        "agent": agent_name,
        "state": "open" if is_open else "closed",
        "failure_count": count,
        "threshold": circuit_breaker.failure_threshold,
        "timeout_seconds": circuit_breaker.timeout,
    }


@app.post("/circuit-breaker/reset/{agent_name}")
async def reset_circuit_breaker(agent_name: str):
    """Manually reset circuit breaker for a specific agent"""
    circuit_breaker.record_success(agent_name)
    logger.info(f"Circuit breaker manually reset for {agent_name}")
    return {"message": f"Circuit breaker reset for {agent_name}"}


@app.post("/heal")
async def trigger_heal(request: HealRequest):
    """Manually trigger healing for a specific agent"""
    logger.info(f"Manual heal requested for {request.agent_name}")
    result = await attempt_heal_agent(
        request.agent_name, 
        request.agent_url, 
        request.attempts, 
        request.timeout
    )
    return result


@app.post("/alerts/webhook")
async def alert_webhook(request: dict):
    """
    Webhook endpoint for Prometheus Alertmanager.
    Triggers auto-healing when specific alerts (e.g., ServiceDown) are received.
    """
    logger.info(f"🔔 Alert webhook received: {len(request.get('alerts', []))} alerts")
    
    for alert in request.get("alerts", []):
        status = alert.get("status")
        labels = alert.get("labels", {})
        alert_name = labels.get("alertname")
        instance = labels.get("instance")
        
        if status == "firing" and alert_name in ["ServiceDown", "ContainerKilled", "ContainerAbsent"]:
            logger.warning(f"🚨 Critical Alert: {alert_name} on {instance}")
            
            # Extract service name from instance (e.g., "healer-agent:8008" -> "healer-agent")
            service_name = instance.split(":")[0] if instance else "unknown"
            
            if service_name != "unknown":
                logger.info(f"Triggering auto-heal for service: {service_name}")
                # Trigger async healing task
                asyncio.create_task(attempt_heal_agent(
                    agent_name=service_name,
                    agent_url=f"http://{instance}", # Assuming internal DNS works
                    attempts=2,
                    timeout=10.0
                ))
    
    return {"status": "processed"}


@app.get("/throttle/state")
async def throttle_state_get():
    return await get_throttle_state()


@app.post("/throttle/state")
async def throttle_state_post(update: ThrottleStateUpdate):
    return await set_throttle_state(update)


async def alert_listener():
    """
    Listens for 'system_alert' messages on Redis pubsub and triggers healing.
    Runs continuously in the background as a coroutine.
    """
    if not redis_client:
        logger.error("Redis client not initialized - cannot start alert listener")
        return
    
    logger.info("Alert listener started - subscribed to 'system_alert' channel")
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("system_alert")
    
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                logger.info(f"📢 Received alert: {message['data']}")
                try:
                    await auto_heal_all()
                except Exception as e:
                    logger.error(f"Error processing alert: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Alert listener crashed: {e}", exc_info=True)
    finally:
        await pubsub.unsubscribe("system_alert")
        logger.warning("Alert listener stopped")


# ============================================
# IMPROVEMENTS IN THIS VERSION:
# ============================================
# 1. ✅ Exponential backoff (2s, 5s, 10s) instead of fixed 5s waits
# 2. ✅ Circuit breaker pattern to prevent infinite retry loops
# 3. ✅ Structured JSON logging for production observability
# 4. ✅ Global timeout (60s) on auto_heal_all to prevent runaway healing
# 5. ✅ Better error handling with specific exception types
# 6. ✅ New endpoints: /circuit-breaker/status and /circuit-breaker/reset
# 7. ✅ Parallel healing with asyncio.gather (already working, kept it)
# 8. ✅ Better logging with success/failure counts
# 9. ✅ Health endpoint shows circuit breaker status
# 10. ✅ Exception handling in alert_listener with try/finally
