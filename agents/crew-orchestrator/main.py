"""
FastAPI Orchestration Layer for HyperCode Agent Crew
Manages communication between 8 specialized agents
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import redis.asyncio as redis
import httpx
import os
import json
from datetime import datetime
import logging
import asyncio
from task_queue import get_redis_pool

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

app = FastAPI(
    title="HyperCode Agent Crew Orchestrator",
    description="Coordinates 8 specialized AI agents for software development",
    version="2.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection for agent communication
redis_client = None

# Agent service endpoints
AGENTS = {
    "project_strategist": "http://project-strategist:8001",
    "frontend_specialist": "http://frontend-specialist:8002",
    "backend_specialist": "http://backend-specialist:8003",
    "database_architect": "http://database-architect:8004",
    "qa_engineer": "http://qa-engineer:8005",
    "devops_engineer": "http://devops-engineer:8006",
    "security_engineer": "http://security-engineer:8007",
    "system_architect": "http://system-architect:8008",
    "coder_agent": "http://coder-agent:8002",
}

# --- WEBSOCKET FOR APPROVALS ---
connected_dashboards: List[WebSocket] = []

@app.websocket("/ws/approvals")
async def websocket_approvals(websocket: WebSocket):
    await websocket.accept()
    connected_dashboards.append(websocket)
    logger.info("Dashboard connected to approval stream")
    
    try:
        # Create a new Redis connection for subscribing
        pubsub_redis = await redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"), decode_responses=True)
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
async def respond_to_approval(response: Dict[str, Any]):
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
    task: TaskDefinition

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

@app.post("/execute")
async def execute_task(request: ExecuteRequest, background_tasks: BackgroundTasks):
    task = request.task
    
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
        approval_id = f"approval-{task.id}"
        approval_request = {
            "id": approval_id,
            "task_id": task.id,
            "description": task.description,
            "agent": task.agent,
            "plan": "Generated plan based on RAG...",
            "risk_level": "Low",
            "estimated_time": "2 minutes"
        }
        
        # Publish to Redis for Dashboard
        if redis_client:
            await redis_client.publish("approval_requests", json.dumps(approval_request))
            await log_event("orchestrator", "warn", f"Approval requested for task {task.id}")
        else:
            logger.error("Redis not connected, cannot request approval")
            return {"status": "error", "message": "Redis disconnected"}
        
        status = "pending"
        timeout = 60
        start_time = datetime.now()
        
        while status == "pending":
            if (datetime.now() - start_time).seconds > timeout:
                await log_event("orchestrator", "error", f"Approval timeout for {task.id}")
                return {"status": "timeout"}
                
            response = await redis_client.get(f"approval:{approval_id}:response")
            if response:
                data = json.loads(response)
                status = data.get("status")
            else:
                await asyncio.sleep(1)
        
        await log_event("orchestrator", "success", f"Approval received: {status}")
        
        if status != "approved":
            return {"status": "rejected"}

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
             approval_id = f"approval-{task.id}-{agent_name}"
             approval_request = {
                "id": approval_id,
                "task_id": task.id,
                "description": f"Execute phase for {agent_name}: {task.description[:50]}...",
                "agent": agent_name,
                "plan": f"Execute specific tasks for {agent_name}",
                "risk_level": "Low",
                "estimated_time": "2 minutes"
             }
             
             if redis_client:
                await redis_client.publish("approval_requests", json.dumps(approval_request))
                await log_event("orchestrator", "warn", f"Approval requested for {agent_name}")
                
                status = "pending"
                timeout = 60
                start_time = datetime.now()
                
                while status == "pending":
                    if (datetime.now() - start_time).seconds > timeout:
                        return {"status": "timeout"}
                    
                    response = await redis_client.get(f"approval:{approval_id}:response")
                    if response:
                        data = json.loads(response)
                        status = data.get("status")
                    else:
                        await asyncio.sleep(1)
                
                if status != "approved":
                    return {"status": "rejected", "agent": agent_name}
                
                await log_event("orchestrator", "success", f"Approved {agent_name}")

        # Determine agent URL
        agent_key = agent_name.replace("-", "_")
        agent_url = AGENTS.get(agent_key)
        
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
                    await log_event(agent_name, "error", f"Failed: {response.text}")
                    results[agent_name] = {"status": "error", "message": f"Agent error: {response.text}"}
                    return {"status": "error", "message": f"Agent {agent_name} failed"}
                    
        except Exception as e:
            await log_event(agent_name, "error", f"Exception: {str(e)}")
            return {"status": "error", "message": str(e)}
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

# --- LIFECYCLE ---

@app.on_event("startup")
async def startup():
    global redis_client
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    redis_client = await redis.from_url(redis_url, decode_responses=True)
    logger.info("✅ Agent Crew Orchestrator started")

@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()

@app.get("/")
async def root():
    return {
        "service": "HyperCode Agent Crew Orchestrator",
        "version": "2.0",
        "agents": list(AGENTS.keys()),
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    try:
        if redis_client:
            await redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# --- DASHBOARD ENDPOINTS ---

@app.get("/agents")
async def get_agents():
    """Get status of all agents"""
    # In a real system, we'd query Prometheus or Docker
    # For now, we return the configured agents with 'idle' status
    # unless we track them in Redis
    
    agents_list = []
    for key, url in AGENTS.items():
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
async def get_tasks():
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
async def get_logs():
    """Get recent system logs"""
    if not redis_client:
        return []
        
    # Get last 50 logs
    logs = await redis_client.lrange("logs:global", 0, 49)
    return [json.loads(log) for log in logs]

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
