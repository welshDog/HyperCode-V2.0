from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
import asyncio
import httpx
import os
import json
import logging
from datetime import datetime
import redis.asyncio as redis
from .adapters.docker_adapter import DockerAdapter
from .models import HealRequest, HealResult

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("healer.main")

app = FastAPI(title="Healer Agent", version="0.1.0", description="Autonomous healing service for agents and systems")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://crew-orchestrator:8080")

redis_client: Optional[redis.Redis] = None
docker_adapter: Optional[DockerAdapter] = None

async def fetch_system_health() -> Dict[str, Dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(f"{ORCHESTRATOR_URL}/system/health")
            if r.status_code != 200:
                logger.error(f"Failed to fetch system health: {r.status_code}")
                return {}
            return r.json()
        except Exception as e:
            logger.error(f"Error fetching system health: {e}")
            return {}

async def ping_agent_health(agent_url: str, timeout: float) -> bool:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(f"{agent_url}/health")
            return r.status_code == 200
    except Exception:
        return False

async def attempt_heal_agent(agent_name: str, agent_url: str, attempts: int, timeout: float) -> HealResult:
    # Phase 1: Check if truly unhealthy
    healthy = await ping_agent_health(agent_url, timeout)
    if healthy:
        return HealResult(agent=agent_name, status="healthy", action="none", details="No action required", timestamp=datetime.now().isoformat())

    # Phase 2: Restart via Docker Adapter
    logger.info(f"Agent {agent_name} is unhealthy. Attempting restart...")
    if docker_adapter:
        restarted = await docker_adapter.restart_container(agent_name)
        if restarted:
             # Wait for startup
            await asyncio.sleep(5.0)
            if await ping_agent_health(agent_url, timeout):
                return HealResult(agent=agent_name, status="recovered", action="restart", details="Restart successful", timestamp=datetime.now().isoformat())
            else:
                 # One retry
                await asyncio.sleep(5.0)
                if await ping_agent_health(agent_url, timeout):
                    return HealResult(agent=agent_name, status="recovered", action="restart", details="Recovered after delay", timestamp=datetime.now().isoformat())
        else:
            return HealResult(agent=agent_name, status="failed", action="restart", details="Restart limit reached or failed", timestamp=datetime.now().isoformat())
    else:
        logger.warning("Docker adapter not initialized")

    return HealResult(agent=agent_name, status="failed", action="restart", details="Agent unresponsive after attempts", timestamp=datetime.now().isoformat())

async def auto_heal_all():
    logger.info("Auto-healing triggered by alert")
    health_data = await fetch_system_health()
    
    tasks = []
    for name, info in health_data.items():
        if info.get("status") == "unhealthy":
            url = info.get("url", f"http://{name}:8000") # Fallback
            tasks.append(attempt_heal_agent(name, url, attempts=2, timeout=5.0))
    
    if tasks:
        results = await asyncio.gather(*tasks)
        for res in results:
            logger.info(f"Heal result for {res.agent}: {res.status} - {res.details}")

@app.on_event("startup")
async def startup():
    global redis_client, docker_adapter
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    docker_adapter = DockerAdapter(redis_url=REDIS_URL)
    
    # Subscribe to orchestrator alerts
    asyncio.create_task(alert_listener())

async def alert_listener():
    pub = await redis.from_url(REDIS_URL, decode_responses=True)
    ps = pub.pubsub()
    await ps.subscribe("approval_requests") 
    
    logger.info("Listening for alerts on Redis...")
    async for message in ps.listen():
        if message.get("type") == "message":
            try:
                data = json.loads(message["data"])
                if data.get("type") == "CRITICAL_ALERT":
                    logger.warning("Received CRITICAL_ALERT. Initiating auto-heal.")
                    await auto_heal_all()
            except Exception as e:
                logger.error(f"Error processing alert: {e}")

@app.get("/health")
async def health():
    docker_ok = False
    if docker_adapter and docker_adapter.client:
        try:
            docker_adapter.client.ping()
            docker_ok = True
        except:
            pass
            
    return {
        "status": "healer_online", 
        "redis": redis_client is not None,
        "docker": docker_ok
    }

@app.post("/heal", response_model=List[HealResult])
async def heal(req: HealRequest):
    logger.info(f"Manual heal request: {req}")
    system = await fetch_system_health()
    
    targets = []
    if req.agents:
        # Filter for requested agents
        for name in req.agents:
            if name in system:
                targets.append((name, system[name]))
            else:
                # Try to heal even if not in system health
                targets.append((name, {"url": f"http://{name}:8000"})) 
    else:
        # Auto-detect unhealthy
        for name, info in system.items():
            if info.get("status") == "unhealthy" or req.force:
                targets.append((name, info))
    
    tasks = []
    for name, info in targets:
        url = info.get("url", f"http://{name}:8000")
        tasks.append(attempt_heal_agent(name, url, attempts=req.retry_attempts, timeout=req.timeout_seconds))
    
    if not tasks:
        return []
        
    results = await asyncio.gather(*tasks)
    return results
