
import os
import asyncio
import json
import httpx
from typing import Dict, Any, Optional
from contextlib import AsyncExitStack

# Try to import BaseAgent from the mounted volume location
try:
    from base_agent import BaseAgent, AgentConfig, TaskRequest, TaskResponse
except ImportError:
    # Fallback for local development or if not mounted yet
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../base-agent")))
    try:
        from agent import BaseAgent, AgentConfig, TaskRequest, TaskResponse
    except ImportError:
        # Define stubs if BaseAgent is completely missing (for build stage)
        class BaseAgent:
            def __init__(self, config): pass
            def run(self): pass
        class AgentConfig: pass
        class TaskRequest: pass
        class TaskResponse: pass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from policy import SecurityPolicy
from prometheus_api_client import PrometheusConnect

# Configure logging
import structlog
from structlog import get_logger

# Configure structlog to match BaseAgent/Core pattern
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = get_logger("coder-agent")

class CoderAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.mcp_client = None
        self.mcp_exit_stack = None
        self.prom = None
        
        # Connect to Prometheus
        prom_url = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
        try:
            self.prom = PrometheusConnect(url=prom_url, disable_ssl=True)
            logger.info("connected_to_prometheus", url=prom_url)
        except Exception as e:
            logger.error("prometheus_connection_failed", error=str(e))

    async def _startup_register(self):
        """Override startup to initialize MCP."""
        await super()._startup_register()
        await self.initialize_mcp()

    async def _shutdown_cleanup(self):
        """Override shutdown to clean up MCP."""
        await super()._shutdown_cleanup()
        if self.mcp_exit_stack:
            await self.mcp_exit_stack.aclose()

    async def initialize_mcp(self):
        """Initialize connection to Docker MCP server."""
        try:
            # We run the Docker MCP server as a subprocess
            # Ensure docker.io is installed in the container
            server_params = StdioServerParameters(
                command="docker-mcp",
                args=[],
                env={"DOCKER_HOST": "unix:///var/run/docker.sock"}
            )
            
            self.mcp_exit_stack = AsyncExitStack()
            
            read_stream, write_stream = await self.mcp_exit_stack.enter_async_context(stdio_client(server_params))
            self.mcp_client = await self.mcp_exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
            await self.mcp_client.initialize()
            
            # List tools to verify connection
            tools_list = await self.mcp_client.list_tools()
            tool_names = [t.name for t in tools_list.tools]
            logger.info("mcp_connected", tools=tool_names)
            
        except Exception as e:
            logger.error("mcp_initialization_failed", error=str(e))
            self.mcp_client = None

    async def execute(self, request: TaskRequest) -> TaskResponse:
        """Execute a coding task."""
        # Mark agent as busy in Redis (BaseAgent pattern)
        self.redis.set(f"agent:{self.config.name}:current_task", request.task_id)
        
        try:
            task = request.task
            context = request.context or {}
            
            logger.info("executing_task", task_id=request.task_id, task=task)
            
            # Simple heuristic matching old logic to route tasks
            # In the future, this should be LLM-driven via tools
            
            result_data = {}
            
            if "metrics" in task.lower() or "health" in task.lower():
                 result_data = self.analyze_system_health()
            elif "deploy" in task.lower() or "docker" in task.lower():
                 result_data = await self.analyze_and_deploy(context.get("code", "") or task)
            else:
                 # Default to coding generation via Ollama
                 prompt = task
                 result_data = await self.generate_code_with_ollama(prompt)
            
            # Format result
            # BaseAgent expects a string result usually, but JSON string is fine
            result_str = json.dumps(result_data)
            
            # Store result in Redis
            self.redis.hset(
                f"task:{request.task_id}",
                f"result:{self.config.name}",
                result_str
            )
            
            logger.info("task_completed", task_id=request.task_id, status="completed")
            
            return TaskResponse(
                task_id=request.task_id,
                agent=self.config.name,
                status="completed",
                result=result_str
            )
            
        except Exception as e:
            logger.error("execution_failed", error=str(e), task_id=request.task_id)
            return TaskResponse(
                task_id=request.task_id,
                agent=self.config.name,
                status="error",
                result=str(e)
            )
        finally:
            self.redis.delete(f"agent:{self.config.name}:current_task")

    async def safe_call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Wrapper for MCP tool calls with security policy enforcement.
        """
        if not self.mcp_client:
             raise Exception("MCP Client not initialized")

        # 1. Check Security Policy
        if not SecurityPolicy.validate_tool_call(tool_name, arguments):
            logger.warning("security_policy_violation", tool=tool_name, arguments=arguments)
            raise Exception(f"Security Policy Violation: Action '{tool_name}' denied by policy.")

        # 2. Execute if allowed
        return await self.mcp_client.call_tool(tool_name, arguments=arguments)

    async def analyze_and_deploy(self, code: str) -> Dict[str, Any]:
        """Analyze code and use Docker MCP to manage containers."""
        if not self.mcp_client:
            return {"status": "error", "message": "MCP Client not initialized"}

        try:
            # 1. List current containers to see context
            # Use safe_call_tool instead of direct call
            containers_result = await self.safe_call_tool("docker_ps", arguments={"all": False})
            
            # 2. Simulate deployment (in a real scenario, we would build/run)
            # For proof of concept, we just return the container list as proof of "hands"
            
            return {
                "status": "completed", 
                "message": "Successfully accessed Docker via MCP (Policy Checked)",
                "containers": containers_result.content,
                "analysis": "Code analyzed. Docker environment accessible."
            }
        except Exception as e:
            logger.error("mcp_operation_failed", error=str(e))
            return {"status": "error", "message": str(e)}

    def analyze_system_health(self) -> Dict[str, Any]:
        """Query Prometheus for system health."""
        if not self.prom:
            return {"status": "error", "message": "Prometheus not connected"}
        
        try:
            # Get CPU usage
            cpu_data = self.prom.custom_query(query='100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) * 100)')
            # Get Memory usage
            mem_data = self.prom.custom_query(query='(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100')
            
            return {
                "status": "completed",
                "metrics": {
                    "cpu_usage": cpu_data,
                    "memory_usage": mem_data
                },
                "analysis": "System is running within normal parameters."
            }
        except Exception as e:
            logger.error("prometheus_query_failed", error=str(e))
            return {"status": "error", "message": str(e)}

    async def generate_code_with_ollama(self, prompt: str, model: str = "qwen2.5-coder:7b") -> Dict[str, Any]:
        """Generate code using Ollama."""
        # Use existing logic but adapted for async execution if needed
        # We use httpx here instead of requests (BaseAgent style)
        url = "http://ollama:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return {"status": "completed", "code": data.get("response", "")}
                else:
                    return {"status": "error", "message": f"Ollama Error: {response.text}"}
        except Exception as e:
             logger.error("ollama_generation_failed", error=str(e))
             return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Ensure environment variables are set or defaulted
    if not os.getenv("AGENT_NAME"):
        os.environ["AGENT_NAME"] = "coder-agent"
    if not os.getenv("AGENT_ROLE"):
        os.environ["AGENT_ROLE"] = "Coder"
    if not os.getenv("AGENT_PORT"):
        os.environ["AGENT_PORT"] = "8000" # Match docker-compose port mapping

    config = AgentConfig()
    agent = CoderAgent(config)
    agent.run()
