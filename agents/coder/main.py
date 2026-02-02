
import asyncio
import aiohttp
import os
import json
import logging
import sys
from prometheus_api_client import PrometheusConnect

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("coder-agent")

CORE_URL = os.getenv("CORE_URL", "http://hypercode-core:8000")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
AGENT_NAME = "Coder"
AGENT_DESCRIPTION = "Specialized agent for code generation and refactoring"
AGENT_TAGS = ["coding", "python", "refactoring", "monitoring"]

class CoderAgent:
    def __init__(self):
        self.id = None
        self.ws = None
        self.session = None
        # Connect to Prometheus
        try:
            self.prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)
            logger.info(f"Connected to Prometheus at {PROMETHEUS_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Prometheus: {e}")
            self.prom = None

    async def register(self):
        """Register the agent with the Core."""
        payload = {
            "name": AGENT_NAME,
            "description": AGENT_DESCRIPTION,
            "version": "0.1.1",
            "endpoint": "http://coder-agent:8000",
            "tags": AGENT_TAGS,
            "capabilities": [
                {"name": "code_generation", "description": "Generate code from prompts", "version": "1.0"},
                {"name": "refactoring", "description": "Refactor code for performance", "version": "1.0"},
                {"name": "analyze_metrics", "description": "Analyze system metrics from Prometheus", "version": "1.0"}
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
        logger.info(f"Executing task: {task}")
        
        task_type = task.get("type", "unknown")
        
        if task_type == "analyze_metrics":
            result = self.analyze_system_health()
        else:
            # Simulation of coding work
            await asyncio.sleep(2)
            result = {"status": "completed", "result": "print('Hello World')"}
        
        logger.info(f"Task completed: {result}")
        # In a real scenario, we would send the result back via WS or API

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
