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

@app.post("/execute")
async def execute_task(request: ExecuteRequest, background_tasks: BackgroundTasks):
    task = request.task
    
    # 1. Log Receipt
    logger.info(json.dumps({
        "event": "task_received",
        "task_id": task.id,
        "agent": task.agent or task.agents
    }))

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
            logger.info(json.dumps({
                "event": "approval_requested", 
                "approval_id": approval_id
            }))
        else:
            logger.error("Redis not connected, cannot request approval")
            return {"status": "error", "message": "Redis disconnected"}
        
        # Wait for approval (Poll Redis)
        # In a real async system, we might return a 'pending' status and let the client poll,
        # but for this test flow we'll block (with timeout) to simulate the 'watch logs' experience.
        status = "pending"
        timeout = 60 # 60 seconds to approve
        start_time = datetime.now()
        
        while status == "pending":
            if (datetime.now() - start_time).seconds > timeout:
                logger.error(f"Approval timeout for {approval_id}")
                return {"status": "timeout"}
                
            response = await redis_client.get(f"approval:{approval_id}:response")
            if response:
                data = json.loads(response)
                status = data.get("status")
            else:
                await asyncio.sleep(1) # Poll every second
        
        logger.info(json.dumps({
            "event": "approval_received",
            "status": status
        }))
        
        if status != "approved":
            return {"status": "rejected"}

    # 5. Execute Agent(s)
    agents_to_run = []
    if task.agents:
        agents_to_run = task.agents
    elif task.agent:
        agents_to_run = [task.agent]
        
    results = {}
    
    for agent_name in agents_to_run:
        logger.info(json.dumps({
            "event": "task_executing",
            "agent": agent_name
        }))
        
        # Approval for multi-agent (Test 2/3)
        # If we have multiple agents, we might want to approve each step or just the whole plan
        # The test description implies "Backend... You approve... Frontend... You approve"
        # So we should probably request approval *per agent* if it's a multi-agent task
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
                logger.info(json.dumps({
                    "event": "approval_requested", 
                    "approval_id": approval_id
                }))
                
                # Wait for approval
                status = "pending"
                timeout = 60
                start_time = datetime.now()
                
                while status == "pending":
                    if (datetime.now() - start_time).seconds > timeout:
                        logger.error(f"Approval timeout for {approval_id}")
                        return {"status": "timeout"}
                    
                    response = await redis_client.get(f"approval:{approval_id}:response")
                    if response:
                        data = json.loads(response)
                        status = data.get("status")
                    else:
                        await asyncio.sleep(1)
                
                logger.info(json.dumps({
                    "event": "approval_received",
                    "status": status
                }))
                
                if status != "approved":
                    return {"status": "rejected", "agent": agent_name}

        # Determine agent URL
        # AGENTS keys are snake_case, task.agent is kebab-case
        agent_key = agent_name.replace("-", "_")
        agent_url = AGENTS.get(agent_key)
        
        if not agent_url:
            # Fallback if not in map
            agent_url = f"http://{agent_name}:8000"

        # Call the agent
        try:
            async with httpx.AsyncClient() as client:
                # The agent expects a TaskRequest structure
                # We need to map our TaskDefinition to the Agent's TaskRequest
                agent_payload = {
                    "id": task.id,
                    "task": task.description,
                    "type": task.type,
                    "requires_approval": False # Already approved by Orchestrator
                }
                
                # Increase timeout for complex tasks
                response = await client.post(f"{agent_url}/execute", json=agent_payload, timeout=120.0)
                if response.status_code == 200:
                    result = response.json()
                    logger.info(json.dumps({
                        "event": "task_completed",
                        "task_id": task.id,
                        "agent": agent_name,
                        "duration": "3.2s", # Mock
                        "result": result
                    }))
                    results[agent_name] = result
                else:
                    logger.error(f"Agent {agent_name} returned {response.status_code}: {response.text}")
                    results[agent_name] = {"status": "error", "message": f"Agent error: {response.text}"}
                    return {"status": "error", "message": f"Agent {agent_name} failed"}
                    
        except Exception as e:
            logger.error(f"Agent {agent_name} execution failed: {e}")
            return {"status": "error", "message": str(e)}

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
