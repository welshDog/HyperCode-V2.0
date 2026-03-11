"""
FastAPI Orchestration Layer for HyperCode Agent Crew
Manages communication between 8 specialized agents
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Request, Depends, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import httpx
import json
import logging
import asyncio
from contextlib import asynccontextmanager
from task_queue import get_redis_pool
import redis.asyncio as redis
from datetime import datetime

# Import configuration
from config import settings

# Configure Logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("crew-orchestrator")

redis_client: Optional[redis.Redis] = None

# Forward declaration of app
app: FastAPI = None # type: ignore

# --- LIFECYCLE ---

async def monitor_agent_health():
    """Background task to monitor agent health status"""
    while True:
        try:
            if not redis_client:
                await asyncio.sleep(5)
                continue
                
            failed_agents = []
            results = {}
            
            for agent_name, url in settings.agents.items():
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        start_time = datetime.now()
                        response = await client.get(f"{url}/health")
                        latency = (datetime.now() - start_time).total_seconds() * 1000
                        
                        if response.status_code == 200:
                            results[agent_name] = {
                                "status": "healthy",
                                "latency_ms": latency,
                                "last_checked": datetime.now().isoformat()
                            }
                        else:
                            failed_agents.append(agent_name)
                            results[agent_name] = {
                                "status": "unhealthy",
                                "error": f"Status {response.status_code}",
                                "last_checked": datetime.now().isoformat()
                            }
                except Exception as e:
                    failed_agents.append(agent_name)
                    results[agent_name] = {
                        "status": "down",
                        "error": str(e),
                        "last_checked": datetime.now().isoformat()
                    }
            
            # Store health results in Redis for dashboard
            await redis_client.set("system:health", json.dumps(results))
            
            # Alert if threshold reached
            if len(failed_agents) >= 4:
                alert_msg = {
                    "type": "CRITICAL_ALERT",
                    "message": f"CRITICAL: {len(failed_agents)} agents are DOWN!",
                    "failed_agents": failed_agents,
                    "timestamp": datetime.now().isoformat()
                }
                # Publish to dashboard via existing approval channel or new alert channel
                await redis_client.publish("approval_requests", json.dumps(alert_msg))
                logger.critical(f"HEALTH ALERT: {len(failed_agents)} agents down: {failed_agents}")
                
        except Exception as e:
            logger.error(f"Health monitor error: {e}")
            
        await asyncio.sleep(30) # Run every 30 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    # Startup
    redis_client = await get_redis_pool()
    logger.info("Redis connected")
    
    # Start background health monitoring
    monitor_task = asyncio.create_task(monitor_agent_health())
    
    yield
    
    # Shutdown
    if monitor_task:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
            
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

app = FastAPI(
    title="HyperCode Agent Crew Orchestrator", 
    description="Coordinates specialized AI agents for software development",
    version="2.0", 
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_allow_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def require_api_key(api_key: str = Security(api_key_header)) -> str:
    expected = settings.api_key
    if not expected:
        return "dev_mode"
    if not api_key or api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key

# --- EXECUTION ENDPOINTS ---

class TaskDefinition(BaseModel):
    id: str
    type: str
    description: str
    agent: Optional[str] = None
    agents: Optional[List[str]] = None
    requires_approval: bool = True
    workflow: Optional[str] = None

class ExecuteRequest(BaseModel):
    task: Optional[Union[TaskDefinition, str]] = None
    id: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    agent: Optional[str] = None
    agents: Optional[List[str]] = None
    agent_type: Optional[str] = None
    task_id: Optional[str] = None
    requires_approval: Optional[bool] = None

# Helper to log to Redis
async def log_event(agent: str, level: str, msg: str):
    if redis_client:
        entry = {
            "id": datetime.now().timestamp(),
            "time": datetime.now().strftime("%H:%M:%S"),
            "agent": agent,
            "level": level,
            "msg": msg
        }
        await redis_client.lpush("logs:global", json.dumps(entry))
        await redis_client.ltrim("logs:global", 0, 99) # Keep last 100

async def request_approval(task_id: str, description: str, agent: Optional[str] = None) -> str:
    """Helper to handle approval workflow"""
    if not redis_client:
        logger.error("Redis not connected, cannot request approval")
        return "error"

    approval_id = f"approval-{task_id}"
    if agent:
        approval_id += f"-{agent}"

    approval_request = {
        "id": approval_id,
        "task_id": task_id,
        "description": description,
        "agent": agent,
        "plan": "Generated plan based on RAG..." if not agent else f"Execute specific tasks for {agent}",
        "risk_level": "Low",
        "estimated_time": "2 minutes"
    }
    
    # Publish to Redis for Dashboard
    await redis_client.publish("approval_requests", json.dumps(approval_request))
    log_msg = f"Approval requested for task {task_id}"
    if agent:
        log_msg += f" ({agent})"
    await log_event("orchestrator", "warn", log_msg)
    
    status = "pending"
    timeout = 60
    start_time = datetime.now()
    
    while status == "pending":
        if (datetime.now() - start_time).seconds > timeout:
            await log_event("orchestrator", "error", f"Approval timeout for {task_id}")
            return "timeout"
            
        response = await redis_client.get(f"approval:{approval_id}:response")
        if response:
            data = json.loads(response)
            status = data.get("status")
        else:
            await asyncio.sleep(1)
    
    await log_event("orchestrator", "success", f"Approval received: {status}")
    return status

@app.post("/execute")
async def execute_task(
    request: ExecuteRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(require_api_key),
):
    task: TaskDefinition
    if isinstance(request.task, TaskDefinition):
        task = request.task
    else:
        legacy_description = request.description
        if not legacy_description and isinstance(request.task, str):
            legacy_description = request.task

        legacy_agent = request.agent or request.agent_type
        legacy_agents = request.agents

        task_id = request.id or request.task_id or f"legacy-{int(datetime.now().timestamp() * 1000)}"
        task_type = request.type or "legacy"
        requires_approval = request.requires_approval if request.requires_approval is not None else False

        if not legacy_description:
            raise HTTPException(status_code=422, detail="Missing task description")

        task = TaskDefinition(
            id=task_id,
            type=task_type,
            description=legacy_description,
            agent=legacy_agent,
            agents=legacy_agents,
            requires_approval=requires_approval,
        )
    
    # 1. Log Receipt
    logger.info(json.dumps({
        "event": "task_received",
        "task_id": task.id,
        "agent": task.agent or task.agents
    }))
    
    # Store Task in Redis
    if redis_client:
        task_data = task.dict()
        task_data["status"] = "in_progress"
        task_data["started_at"] = datetime.now().isoformat()
        task_data["progress"] = 0
        task_data["steps"] = task.agents or [task.agent]
        await redis_client.set(f"task:{task.id}:details", json.dumps(task_data))
        await redis_client.lpush("tasks:history", task.id)
        await redis_client.ltrim("tasks:history", 0, 99)
        
        await log_event("orchestrator", "info", f"Received task: {task.id}")

    # 2. RAG Query (Simulated for Test 1)
    logger.info(json.dumps({
        "event": "rag_query",
        "query": task.description[:50],
        "chunks_retrieved": 3
    }))
    
    # 3. Plan Generation (Simulated for Test 1)
    logger.info(json.dumps({
        "event": "plan_generated",
        "task_id": task.id
    }))

    # 4. Approval Flow
    if task.requires_approval:
        status = await request_approval(task.id, task.description, task.agent)
        if status != "approved":
            return {"status": "rejected" if status != "timeout" else "timeout"}

    # 5. Execute Agent(s)
    agents_to_run = []
    if task.agents:
        agents_to_run = task.agents
    elif task.agent:
        agents_to_run = [task.agent]
        
    results = {}
    
    # Update progress
    if redis_client:
        task_data = json.loads(await redis_client.get(f"task:{task.id}:details"))
        task_data["progress"] = 10
        await redis_client.set(f"task:{task.id}:details", json.dumps(task_data))
    
    for i, agent_name in enumerate(agents_to_run):
        await log_event(agent_name, "info", f"Starting execution phase {i+1}/{len(agents_to_run)}")
        
        # Mark agent as busy
        if redis_client:
            await redis_client.set(f"agent:{agent_name}:current_task", task.id)
            
            # Update progress
            task_data = json.loads(await redis_client.get(f"task:{task.id}:details"))
            task_data["progress"] = 10 + int((i / len(agents_to_run)) * 80)
            await redis_client.set(f"task:{task.id}:details", json.dumps(task_data))

        # Approval for multi-agent (Test 2/3)
        if len(agents_to_run) > 1 and task.requires_approval:
             desc = f"Execute phase for {agent_name}: {task.description[:50]}..."
             status = await request_approval(task.id, desc, agent_name)
             
             if status != "approved":
                 return {"status": "rejected" if status != "timeout" else "timeout", "agent": agent_name}

        # Determine agent URL
        agent_key = agent_name.replace("-", "_")
        agent_url = settings.agents.get(agent_key)
        
        if not agent_url:
            agent_url = f"http://{agent_name}:8000"

        # Call the agent
        try:
            async with httpx.AsyncClient() as client:
                agent_payload = {
                    "id": task.id,
                    "task": task.description,
                    "type": task.type,
                    "requires_approval": False
                }
                
                response = await client.post(f"{agent_url}/execute", json=agent_payload, timeout=120.0)
                if response.status_code == 200:
                    result = response.json()
                    await log_event(agent_name, "success", "Task completed successfully")
                    results[agent_name] = result
                else:
                    await log_event(agent_name, "error", f"Failed: status={response.status_code}")
                    results[agent_name] = {"status": "error", "message": "Agent execution failed"}
                    return {"status": "error", "message": "Agent execution failed"}
                    
        except Exception as e:
            await log_event(agent_name, "error", "Exception during agent execution")
            logger.exception("Agent execution exception")
            return {"status": "error", "message": "Agent execution failed"}
        finally:
            # Mark agent as idle
            if redis_client:
                await redis_client.delete(f"agent:{agent_name}:current_task")

    # Final update
    if redis_client:
        task_data = json.loads(await redis_client.get(f"task:{task.id}:details"))
        task_data["progress"] = 100
        task_data["status"] = "completed"
        await redis_client.set(f"task:{task.id}:details", json.dumps(task_data))
        await log_event("orchestrator", "success", "Workflow completed")

    return {"status": "completed", "message": "Workflow finished", "results": results}

# --- WEBSOCKET FOR APPROVALS ---
connected_dashboards: List[WebSocket] = []

# --- WEBSOCKETS ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> bool:
        expected = settings.api_key
        if expected:
            provided = websocket.headers.get("x-api-key") or websocket.query_params.get("api_key")
            if provided != expected:
                await websocket.accept()
                await websocket.close(code=1008)
                return False
        await websocket.accept()
        self.active_connections.append(websocket)
        return True

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")

manager = ConnectionManager()

@app.websocket("/ws/uplink")
async def websocket_endpoint(websocket: WebSocket):
    if not await manager.connect(websocket):
        return
    try:
        while True:
            data = await websocket.receive_text()
            # Echo for now, or process command
            try:
                message = json.loads(data)
                response = {
                    "id": message.get("id"),
                    "type": "response",
                    "source": "orchestrator", 
                    "payload": {"status": "received", "echo": message.get("payload")}
                }
                await websocket.send_text(json.dumps(response))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "payload": "Invalid JSON"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from uplink")

@app.websocket("/ws/approvals")
async def websocket_approvals(websocket: WebSocket):
    expected = settings.api_key
    if expected:
        provided = websocket.headers.get("x-api-key") or websocket.query_params.get("api_key")
        if provided != expected:
            await websocket.accept()
            await websocket.close(code=1008)
            return
    await websocket.accept()
    connected_dashboards.append(websocket)
    logger.info("Dashboard connected to approval stream")
    
    try:
        # Create a new Redis connection for subscribing
        pubsub_redis = await redis.from_url(settings.redis_url, decode_responses=True)
        pubsub = pubsub_redis.pubsub()
        await pubsub.subscribe("approval_requests")
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                # Forward approval request to dashboard
                await websocket.send_text(message['data'])
                
    except WebSocketDisconnect:
        logger.info("Dashboard disconnected")
        connected_dashboards.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in connected_dashboards:
            connected_dashboards.remove(websocket)

@app.post("/approvals/respond")
async def respond_to_approval(
    response: Dict[str, Any],
    api_key: str = Depends(require_api_key),
):
    """Endpoint for Dashboard to approve/reject tasks"""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not connected")
        
    approval_id = response.get("approval_id")
    if not approval_id:
        raise HTTPException(status_code=400, detail="Missing approval_id")
        
    # Store the response where the waiting agent can find it
    await redis_client.set(
        f"approval:{approval_id}:response",
        json.dumps(response),
        ex=3600 # Expire in 1 hour
    )
    
    return {"status": "response_recorded"}

@app.get("/system/health")
async def get_system_health(api_key: str = Depends(require_api_key)):
    """Return cached health data for all agents"""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not connected")
        
    health_data = await redis_client.get("system:health")
    if not health_data:
        return {"status": "initializing", "agents": {}}
        
    return json.loads(health_data)



@app.get("/")
async def root():
    return {
        "service": "HyperCode Agent Crew Orchestrator",
        "version": "2.0",
        "agents": list(settings.agents.keys()),
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Simple health check endpoint for Docker"""
    return {"status": "ok", "service": "crew-orchestrator"}

# --- DASHBOARD ENDPOINTS ---

@app.get("/agents")
async def get_agents(api_key: str = Depends(require_api_key)):
    """Get status of all agents"""
    # In a real system, we'd query Prometheus or Docker
    # For now, we return the configured agents with 'idle' status
    # unless we track them in Redis
    
    agents_list = []
    for key, url in settings.agents.items():
        # Clean up name
        name = key.replace("_", " ").title()
        role = key.split("_")[-1].title() if "_" in key else "Agent"
        
        # Check Redis for status if available
        status = "idle"
        cpu = 0
        ram = 0
        
        if redis_client:
            # Check if agent is busy
            # This key would be set during execution
            current_task = await redis_client.get(f"agent:{key}:current_task")
            if current_task:
                status = "working"
                cpu = 45 + (len(name) * 2) # Mock variation
                ram = 30 + (len(name) * 3)
            else:
                # Mock idle stats
                cpu = 1 + (len(name) % 5)
                ram = 10 + (len(name) % 10)
                
        agents_list.append({
            "id": key,
            "name": name,
            "role": role,
            "status": status,
            "cpu": cpu,
            "ram": ram,
            "url": url
        })
        
    return agents_list

@app.get("/tasks")
async def get_tasks(api_key: str = Depends(require_api_key)):
    """Get recent tasks"""
    if not redis_client:
        return []
        
    # Get last 10 tasks from a list
    task_ids = await redis_client.lrange("tasks:history", 0, 9)
    tasks = []
    
    for tid in task_ids:
        task_data = await redis_client.get(f"task:{tid}:details")
        if task_data:
            tasks.append(json.loads(task_data))
            
    return tasks

@app.get("/logs")
async def get_logs(api_key: str = Depends(require_api_key)):
    """Get recent system logs"""
    if not redis_client:
        return []
        
    # Get last 50 logs
    logs = await redis_client.lrange("logs:global", 0, 49)
    return [json.loads(log) for log in logs]
