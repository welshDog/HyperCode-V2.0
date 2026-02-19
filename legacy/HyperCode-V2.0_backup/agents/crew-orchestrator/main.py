"""
FastAPI Orchestration Layer for HyperCode Agent Crew
Manages communication between 8 specialized agents
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import redis.asyncio as redis
import httpx
import os
import json
from datetime import datetime

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
}

# Request Models
class TaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None
    priority: str = "normal"
    files: Optional[List[str]] = None

class AgentMessage(BaseModel):
    agent: str
    message: str
    context: Optional[Dict[str, Any]] = None

class WorkflowRequest(BaseModel):
    workflow_type: str  # "feature", "bugfix", "refactor"
    description: str
    requirements: Optional[Dict[str, Any]] = None

# Response Models
class TaskResponse(BaseModel):
    task_id: str
    status: str
    assigned_agents: List[str]
    estimated_time: str

class AgentStatus(BaseModel):
    agent: str
    status: str
    current_task: Optional[str]
    last_activity: str


@app.on_event("startup")
async def startup():
    global redis_client
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    redis_client = await redis.from_url(redis_url, decode_responses=True)
    print("✅ Agent Crew Orchestrator started")

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
    """Health check endpoint"""
    try:
        await redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unhealthy: {str(e)}")

@app.post("/plan", response_model=TaskResponse)
async def plan_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Send task to Project Strategist for planning and delegation
    """
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Store task in Redis
    await redis_client.hset(
        f"task:{task_id}",
        mapping={
            "description": request.task,
            "status": "planning",
            "created_at": datetime.now().isoformat(),
            "context": json.dumps(request.context or {})
        }
    )
    
    # Send to Project Strategist
    background_tasks.add_task(
        delegate_to_strategist,
        task_id,
        request.task,
        request.context
    )
    
    return TaskResponse(
        task_id=task_id,
        status="planning",
        assigned_agents=["project_strategist"],
        estimated_time="Calculating..."
    )

@app.post("/agent/{agent_name}/execute")
async def execute_agent_task(agent_name: str, message: AgentMessage):
    """
    Direct execution of a specific agent task
    """
    if agent_name not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AGENTS[agent_name]}/execute",
                json=message.dict(),
                timeout=120.0
            )
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Agent {agent_name} unreachable: {str(e)}")

@app.post("/workflow/{workflow_type}")
async def start_workflow(workflow_type: str, request: WorkflowRequest):
    """
    Start a predefined workflow (feature, bugfix, refactor)
    """
    workflows = {
        "feature": ["project_strategist", "system_architect", "frontend_specialist", 
                   "backend_specialist", "database_architect", "qa_engineer", "devops_engineer"],
        "bugfix": ["project_strategist", "qa_engineer", "backend_specialist", "frontend_specialist"],
        "refactor": ["system_architect", "backend_specialist", "frontend_specialist", "qa_engineer"],
        "security_audit": ["security_engineer", "backend_specialist", "database_architect"]
    }
    
    if workflow_type not in workflows:
        raise HTTPException(status_code=400, detail=f"Unknown workflow: {workflow_type}")
    
    workflow_id = f"workflow_{workflow_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Store workflow
    await redis_client.hset(
        f"workflow:{workflow_id}",
        mapping={
            "type": workflow_type,
            "description": request.description,
            "agents": json.dumps(workflows[workflow_type]),
            "status": "initiated",
            "created_at": datetime.now().isoformat()
        }
    )
    
    return {
        "workflow_id": workflow_id,
        "type": workflow_type,
        "agents": workflows[workflow_type],
        "status": "initiated"
    }

@app.get("/agents/status")
async def get_agents_status():
    """
    Get status of all agents
    """
    statuses = []
    async with httpx.AsyncClient() as client:
        for agent_name, endpoint in AGENTS.items():
            try:
                response = await client.get(f"{endpoint}/status", timeout=5.0)
                statuses.append({
                    "agent": agent_name,
                    "status": "online",
                    "data": response.json()
                })
            except Exception as e:
                statuses.append({
                    "agent": agent_name,
                    "status": "offline",
                    "error": str(e)
                })
    return statuses

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get status of a specific task
    """
    task_data = await redis_client.hgetall(f"task:{task_id}")
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task_id,
        **task_data
    }

@app.get("/memory/standards")
async def get_team_standards():
    """
    Retrieve shared Team Memory Standards (Hive Mind)
    """
    try:
        with open("/app/hive_mind/Team_Memory_Standards.md", "r") as f:
            standards = f.read()
        return {"standards": standards}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Team standards not found")

@app.get("/skills")
async def get_agent_skills():
    """
    Retrieve Agent Skills Library
    """
    try:
        with open("/app/hive_mind/Agent_Skills_Library.md", "r") as f:
            skills = f.read()
        return {"skills": skills}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Skills library not found")

# Background task functions
async def delegate_to_strategist(task_id: str, task: str, context: Optional[Dict]):
    """
    Send task to Project Strategist for breakdown and delegation
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AGENTS['project_strategist']}/plan",
                json={
                    "task_id": task_id,
                    "task": task,
                    "context": context
                },
                timeout=120.0
            )
            
            # Update task status
            await redis_client.hset(
                f"task:{task_id}",
                "status",
                "delegated"
            )
            
            # Store planning result
            await redis_client.hset(
                f"task:{task_id}",
                "plan",
                json.dumps(response.json())
            )
    except Exception as e:
        await redis_client.hset(
            f"task:{task_id}",
            "status",
            f"error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
