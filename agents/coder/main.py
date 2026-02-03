
import asyncio
import aiohttp
import os
import json
import logging
import sys
from prometheus_api_client import PrometheusConnect
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from policy import SecurityPolicy

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("coder-agent")

# Initialize OpenTelemetry
resource = Resource(attributes={
    "service.name": "coder-agent",
    "service.version": "0.2.0"
})
trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))
tracer = trace.get_tracer(__name__)

# Instrument aiohttp client
AioHttpClientInstrumentator().instrument()
CORE_URL = os.getenv("CORE_URL", "http://hypercode-core:8000")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
AGENT_NAME = "Coder"
AGENT_DESCRIPTION = "Specialized agent for code generation, refactoring, and infrastructure management"
AGENT_TAGS = ["coding", "python", "refactoring", "monitoring", "docker", "mcp"]

class CoderAgent:
    def __init__(self):
        self.id = None
        self.ws = None
        self.session = None
        self.mcp_client = None
        self.mcp_exit_stack = None
        
        # Connect to Prometheus
        try:
            self.prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)
            logger.info(f"Connected to Prometheus at {PROMETHEUS_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Prometheus: {e}")
            self.prom = None

    async def initialize_mcp(self):
        """Initialize connection to Docker MCP server."""
        try:
            # We run the Docker MCP server as a subprocess
            # Using the installed python package 'docker-mcp'
            server_params = StdioServerParameters(
                command="docker-mcp",
                args=[],
                env={"DOCKER_HOST": "unix:///var/run/docker.sock"}
            )
            
            # Start the client
            # Note: stdio_client is a context manager, so we need to manage its lifecycle manually 
            # or keep it open for the duration of the agent's life.
            # For simplicity in this structure, we'll enter the context and keep it.
            # In a robust implementation, we might want to use AsyncExitStack.
            from contextlib import AsyncExitStack
            self.mcp_exit_stack = AsyncExitStack()
            
            read_stream, write_stream = await self.mcp_exit_stack.enter_async_context(stdio_client(server_params))
            self.mcp_client = await self.mcp_exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
            await self.mcp_client.initialize()
            
            logger.info("Successfully connected to Docker MCP Server")
            
            # List tools to verify connection
            tools = await self.mcp_client.list_tools()
            logger.info(f"Available MCP tools: {[tool.name for tool in tools.tools]}")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP: {e}")
            self.mcp_client = None

    async def register(self):
        """Register the agent with the Core."""
        payload = {
            "name": AGENT_NAME,
            "description": AGENT_DESCRIPTION,
            "version": "0.2.0",
            "endpoint": "http://coder-agent:8000",
            "tags": AGENT_TAGS,
            "capabilities": [
                {"name": "code_generation", "description": "Generate code from prompts", "version": "1.0"},
                {"name": "refactoring", "description": "Refactor code for performance", "version": "1.0"},
                {"name": "analyze_metrics", "description": "Analyze system metrics from Prometheus", "version": "1.0"},
                {"name": "analyze_and_deploy", "description": "Analyze code and manage containers via MCP", "version": "1.0"}
            ]
        }
        
        try:
            # We need a session for registration
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{CORE_URL}/agents/register", json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.id = data["id"]
                        logger.info(f"Registered Coder Agent with ID: {self.id}")
                        return True
                    else:
                        logger.error(f"Registration failed: {resp.status} - {await resp.text()}")
                        return False
        except Exception as e:
            logger.error(f"Failed to connect to Core: {e}")
            return False

    async def connect_ws(self):
        """Connect to the Core WebSocket channel."""
        if not self.id:
            return
            
        # Initialize MCP before connecting to WS
        await self.initialize_mcp()

        ws_url = f"{CORE_URL}/agents/{self.id}/channel".replace("http", "ws")
        try:
            self.session = aiohttp.ClientSession()
            async with self.session.ws_connect(ws_url) as ws:
                self.ws = ws
                logger.info("WebSocket connected")
                
                # Heartbeat loop
                while True:
                    await ws.send_str("ping")
                    msg = await ws.receive()
                    
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        if msg.data == "pong":
                            logger.debug("Heartbeat pong received")
                        else:
                            await self.on_message(msg.data)
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        logger.warning("WebSocket closed")
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error("WebSocket error")
                        break
                    
                    await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            if self.session:
                await self.session.close()
            # Clean up MCP connection
            if self.mcp_exit_stack:
                await self.mcp_exit_stack.aclose()

    async def on_message(self, message):
        """Handle incoming tasks."""
        logger.info(f"Received message: {message}")
        try:
            data = json.loads(message)
            if data.get("type") == "task":
                await self.on_task(data.get("payload"))
        except json.JSONDecodeError:
            pass

    async def on_task(self, task):
        """Execute a coding task."""
        with tracer.start_as_current_span("execute_task") as span:
            span.set_attribute("task.type", task.get("type", "unknown"))
            logger.info(f"Executing task: {task}")
            
            task_type = task.get("type", "unknown")
            
            if task_type == "analyze_metrics":
                result = self.analyze_system_health()
            elif task_type == "analyze_and_deploy":
                result = await self.analyze_and_deploy(task.get("code", ""))
            else:
                # Simulation of coding work
                await asyncio.sleep(2)
                result = {"status": "completed", "result": "print('Hello World')"}
            
            span.set_attribute("task.status", result.get("status"))
            logger.info(f"Task completed: {result}")
            # In a real scenario, we would send the result back via WS or API

    async def safe_call_tool(self, tool_name, arguments):
        """
        Wrapper for MCP tool calls with security policy enforcement.
        """
        if not self.mcp_client:
             raise Exception("MCP Client not initialized")

        # 1. Check Security Policy
        if not SecurityPolicy.validate_tool_call(tool_name, arguments):
            raise Exception(f"Security Policy Violation: Action '{tool_name}' denied by policy.")

        # 2. Execute if allowed
        return await self.mcp_client.call_tool(tool_name, arguments=arguments)

    async def analyze_and_deploy(self, code):
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
            logger.error(f"MCP Operation failed: {e}")
            return {"status": "error", "message": str(e)}

    def analyze_system_health(self):
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
                "analysis": "System is running within normal parameters." # Placeholder logic
            }
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    agent = CoderAgent()
    loop = asyncio.get_event_loop()
    
    if loop.run_until_complete(agent.register()):
        loop.run_until_complete(agent.connect_ws())
