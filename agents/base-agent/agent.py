"""
Base Agent Template for HyperCode Crew
Each specialized agent extends this base
"""
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import asyncio
import httpx
import redis
from anthropic import Anthropic
from datetime import datetime
import json

class AgentConfig:
    """Base configuration for all agents"""
    def __init__(self):
        self.name = os.getenv("AGENT_NAME", "base-agent")
        self.role = os.getenv("AGENT_ROLE", "Generic Agent")
        self.model = os.getenv("AGENT_MODEL", "claude-3-5-sonnet-20241022")
        self.port = int(os.getenv("AGENT_PORT", "8001"))
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        self.core_url = os.getenv("CORE_URL", "http://hypercode-core:8000")
        self.health_url = os.getenv("AGENT_HEALTH_URL", f"http://localhost:{self.port}/health")
        self.api_key = os.getenv("HYPERCODE_API_KEY")
        
        # Load Hive Mind standards
        self.load_hive_mind()
    
    def load_hive_mind(self):
        """Load Team Memory Standards and Skills"""
        try:
            with open("/app/hive_mind/Team_Memory_Standards.md", "r") as f:
                self.team_standards = f.read()
            with open("/app/hive_mind/Agent_Skills_Library.md", "r") as f:
                self.skills_library = f.read()
        except FileNotFoundError:
            print("⚠️ Hive Mind files not found, using defaults")
            self.team_standards = ""
            self.skills_library = ""

    def load_capabilities(self) -> list[str]:
        try:
            import json
            with open("/app/config.json", "r") as f:
                cfg = json.load(f)
            specs = cfg.get("specializations") or []
            return [str(s).lower() for s in specs]
        except Exception:
            return []

class TaskRequest(BaseModel):
    task_id: str
    task: str
    context: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    task_id: str
    agent: str
    status: str
    result: Optional[str] = None
    artifacts: Optional[List[str]] = None

class BaseAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.app = FastAPI(title=f"{config.name} Agent")
        self.client = Anthropic(api_key=config.anthropic_key)
        self.redis = redis.from_url(config.redis_url, decode_responses=True)
        self._agent_id: str | None = None
        self._heartbeat_task: asyncio.Task | None = None
        
        # Register routes
        self.setup_routes()
    
    def setup_routes(self):
        async def verify_api_key(api_key: str = Security(APIKeyHeader(name="X-API-Key", auto_error=True))):
            if self.config.api_key and api_key != self.config.api_key:
                raise HTTPException(status_code=403, detail="Invalid API Key")
            return api_key

        @self.app.get("/")
        async def root():
            return {
                "agent": self.config.name,
                "role": self.config.role,
                "model": self.config.model,
                "status": "ready"
            }
        
        @self.app.get("/health")
        async def health():
            try:
                self.redis.ping()
                return {"status": "healthy", "redis": "connected"}
            except Exception as e:
                raise HTTPException(status_code=503, detail=str(e))
        
        @self.app.get("/status")
        async def status():
            current_task = self.redis.get(f"agent:{self.config.name}:current_task")
            return {
                "agent": self.config.name,
                "status": "busy" if current_task else "idle",
                "current_task": current_task,
                "last_activity": datetime.now().isoformat()
            }

        @self.app.on_event("startup")
        async def _startup_register():
            await self._register_with_core()
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        @self.app.on_event("shutdown")
        async def _shutdown_cleanup():
            try:
                if self._heartbeat_task:
                    self._heartbeat_task.cancel()
            except Exception:
                pass
        
        @self.app.post("/execute", response_model=TaskResponse)
        async def execute_task(request: TaskRequest):
            return await self.execute(request)
        
        @self.app.post("/plan")
        async def plan_task(request: TaskRequest):
            """Project Strategist specific endpoint"""
            return await self.plan(request)
    
    async def execute(self, request: TaskRequest) -> TaskResponse:
        """
        Main execution logic - override in specialized agents
        """
        # Mark agent as busy
        self.redis.set(f"agent:{self.config.name}:current_task", request.task_id)
        
        try:
            # Build context with Hive Mind
            system_prompt = self.build_system_prompt()
            
            # --- SWARM MEMORY RECALL ---
            try:
                memories = await self.recall(request.task, limit=3)
                if memories:
                    memory_context = "\n".join([f"- {m.get('content')} (Score: {m.get('metadata', {}).get('score', 0):.2f})" for m in memories])
                    system_prompt += f"\n\n**Relevant Team Memories:**\n{memory_context}\n"
                    print(f"🧠 {self.config.name} recalled {len(memories)} memories for task {request.task_id}")
            except Exception as e:
                print(f"⚠️ Memory recall failed: {e}")
            # ---------------------------

            # Call Claude
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Task: {request.task}\n\nContext: {json.dumps(request.context or {})}"
                }]
            )
            
            result = message.content[0].text
            
            # Store result in Redis
            self.redis.hset(
                f"task:{request.task_id}",
                f"result:{self.config.name}",
                result
            )
            
            # --- SWARM MEMORY REMEMBER ---
            try:
                # Only remember significant results (heuristic: length > 50 chars)
                if len(result) > 50:
                    await self.remember(
                        content=f"Task: {request.task}\nResult: {result[:500]}...", # Truncate for summary
                        keywords=["task_result", self.config.role],
                        metadata={"task_id": request.task_id, "full_result_length": len(result)}
                    )
                    print(f"💾 {self.config.name} stored memory for task {request.task_id}")
            except Exception as e:
                print(f"⚠️ Memory storage failed: {e}")
            # -----------------------------

            return TaskResponse(
                task_id=request.task_id,
                agent=self.config.name,
                status="completed",
                result=result
            )
        
        except Exception as e:
            return TaskResponse(
                task_id=request.task_id,
                agent=self.config.name,
                status="error",
                result=str(e)
            )
        finally:
            # Mark agent as idle
            self.redis.delete(f"agent:{self.config.name}:current_task")
    
    async def plan(self, request: TaskRequest) -> Dict:
        """
        Planning logic for Project Strategist
        """
        # To be implemented by Project Strategist agent
        return {"status": "not_implemented"}
    
    def build_system_prompt(self) -> str:
        """
        Build system prompt with role, standards, and skills
        """
        return f"""You are {self.config.role} in the HyperCode development team.

**Team Standards:**
{self.config.team_standards}

**Available Skills:**
{self.config.skills_library}

Follow these standards strictly and leverage the skills library when applicable.
"""

    async def remember(self, content: str, keywords: List[str] = [], metadata: Dict = {}):
        """Store a memory in the Swarm Memory"""
        try:
            payload = {
                "content": content,
                "keywords": keywords,
                "metadata": {**metadata, "agent": self.config.name, "role": self.config.role},
                "type": "observation"
            }
            async with httpx.AsyncClient() as client:
                await client.post(f"{self.config.core_url}/memory/", json=payload)
        except Exception as e:
            print(f"⚠️ Failed to remember: {e}")

    async def recall(self, query: str, limit: int = 5) -> List[Dict]:
        """Recall memories from the Swarm Memory"""
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{self.config.core_url}/memory/search", params={"query": query, "limit": limit})
                if res.status_code == 200:
                    return res.json()
            return []
        except Exception as e:
            print(f"⚠️ Failed to recall: {e}")
            return []
    
    def run(self):
        """Start the agent service"""
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=self.config.port)

    async def _register_with_core(self):
        """Attempts to register the agent with Core. Returns True on success."""
        try:
            print(f"🔄 Attempting to register {self.config.name} with Core at {self.config.core_url}...")
            payload = {
                "name": self.config.name,
                "role": (self.config.role or "general").lower(),
                "version": "1.0.0",
                "capabilities": self.config.load_capabilities(),
                "topics": ["agent.events"],
                "health_url": self.config.health_url,
                "dedup_key": self.config.name,
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(f"{self.config.core_url}/agents/register", json=payload)
                if r.status_code in (200, 201, 204):
                    data = r.json()
                    self._agent_id = data.get("id")
                    print(f"✅ Successfully registered agent: {self.config.name} (ID: {self._agent_id})")
                    return True
                else:
                    print(f"⚠️ Registration failed with status {r.status_code}: {r.text}")
        except Exception as e:
            print(f"⚠️ Agent registration connection failed: {e}")
        return False

    async def _heartbeat_loop(self):
        """Sends periodic heartbeats, handling registration if needed."""
        print(f"💓 Starting heartbeat loop for {self.config.name}...")
        while True:
            try:
                # If not registered, try to register first
                if not self._agent_id:
                    success = await self._register_with_core()
                    if not success:
                        await asyncio.sleep(5)  # Retry registration sooner
                        continue

                # Send heartbeat
                if self._agent_id:
                    payload = {"agent_id": self._agent_id, "status": "active", "load": 0.0}
                    
                    # Add API Key if available
                    headers = {}
                    if self.config.api_key:
                        headers["X-API-Key"] = self.config.api_key

                    async with httpx.AsyncClient(timeout=5.0) as client:
                        r = await client.post(f"{self.config.core_url}/agents/heartbeat", json=payload, headers=headers)
                        if r.status_code == 404:
                            # Agent ID not found (maybe core restarted), re-register
                            print(f"⚠️ Core lost agent {self._agent_id}, re-registering...")
                            self._agent_id = None
                        elif r.status_code != 200:
                            print(f"⚠️ Heartbeat failed: {r.status_code}")
                
                await asyncio.sleep(10) # Heartbeat every 10s
            except asyncio.CancelledError:
                print("🛑 Heartbeat loop cancelled")
                break
            except Exception as e:
                print(f"⚠️ Heartbeat error: {e}")
                await asyncio.sleep(10)

if __name__ == "__main__":
    config = AgentConfig()
    agent = BaseAgent(config)
    agent.run()
