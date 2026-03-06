import json
import logging
import os
import sys
import argparse
import time
import redis
import requests
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "business-agent.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ProjectStrategist")

class ProjectStrategistAgent:
    """
    Project Strategist Agent
    Core responsibilities:
    - Aligns project goals with execution plans
    - Manages milestones
    - Ensures strategic coherence
    """

    def __init__(self, config_path: str = None):
        """
        Initialize the agent.
        :param config_path: Path to the configuration JSON file.
        """
        self.config = {}
        self.state = "IDLE"
        self._load_config(config_path)
        self.initialize()

    def _load_config(self, config_path: Optional[str]):
        """
        Load configuration from a JSON file.
        """
        if not config_path:
            # Default relative path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "business-agent.json")

        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
        except FileNotFoundError:
            logger.error(f"Configuration file not found at {config_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file at {config_path}")
            raise

    def initialize(self):
        """
        Lifecycle method: Initialize agent resources.
        """
        logger.info(f"Initializing {self.config.get('name', 'Unknown Agent')}...")
        self.state = "INITIALIZING"
        
        # Load capabilities
        self.capabilities = self.config.get("capabilities", [])
        
        # Initialize Redis
        self._init_redis()
        
        self.state = "READY"
        logger.info("Agent initialized and READY.")

    def _init_redis(self):
        """
        Initialize Redis connection with retry logic.
        """
        redis_conf = self.config.get("redis_config", {})
        # If running in Docker, use the service name 'redis' instead of localhost
        # We can detect this via an env var or just default to 'redis' if 'localhost' fails
        host = os.environ.get("REDIS_HOST", "localhost")
        port = int(os.environ.get("REDIS_PORT", 6379))
        db = redis_conf.get("db", 0)
        password = redis_conf.get("password")

        # Skip actual connection if in test mode or explicitly disabled
        # This is a simple way to allow unit tests to pass without a running Redis
        if os.environ.get("TEST_MODE") == "true":
            logger.info("TEST_MODE detected. Skipping Redis connection.")
            self.redis_client = None
            return

        # Simple retry loop with exponential backoff for initial connection
        max_retries = 5
        retry_delay = 2
        
        for i in range(max_retries):
            try:
                logger.info(f"Connecting to Redis at {host}:{port} (Attempt {i+1}/{max_retries})...")
                self.redis_client = redis.Redis(
                    host=host, 
                    port=port, 
                    db=db, 
                    password=password, 
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                self.redis_client.ping()
                logger.info(f"Connected to Redis at {host}:{port}")
                return
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning(f"Failed to connect to Redis at {host}:{port}: {e}")
                if i < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Could not connect to Redis after {max_retries} attempts.")
                    self.redis_client = None
                    # In production, we might want to crash here if Redis is critical
                    # raise e

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), retry=retry_if_exception_type((requests.RequestException, TimeoutError)))
    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM service with retry logic.
        """
        llm_conf = self.config.get("llm_config", {})
        model = llm_conf.get("model", "gpt-4-turbo")
        # Assuming a local or proxy LLM endpoint for now, or direct API
        # Replacing with actual implementation logic:
        
        # NOTE: This is a placeholder for the actual API call. 
        # In a real scenario, this would use the OpenAI SDK or a request to the Core API.
        # For prototype, we simulate a successful response if 'mock' is not enabled.
        
        # Simulation delay to test timeout handling
        # time.sleep(0.1) 
        
        logger.info(f"Calling LLM ({model}) with prompt length: {len(prompt)}")
        return f"Simulated LLM response for: {prompt[:50]}..."

    def publish_message(self, channel: str, message: Dict[str, Any]):
        """
        Publish a message to Redis.
        """
        if not self.redis_client:
            logger.warning("Redis client not available. Skipping publish.")
            return

        try:
            start_time = time.time()
            self.redis_client.publish(channel, json.dumps(message))
            latency = (time.time() - start_time) * 1000
            logger.info(f"Published to {channel} in {latency:.2f}ms")
        except Exception as e:
            logger.error(f"Failed to publish to Redis: {e}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lifecycle method: Execute a task.
        :param task: A dictionary containing task details.
        :return: Result dictionary.
        """
        if self.state != "READY":
            msg = f"Agent is not ready. Current state: {self.state}"
            logger.warning(msg)
            return {"status": "error", "message": msg}

        self.state = "WORKING"
        task_id = task.get("id", "unknown")
        task_type = task.get("type", "unknown")
        logger.info(f"Executing task: {task_type} (ID: {task_id})")

        try:
            # 1. Analyze Task with LLM
            prompt = f"Analyze strategy for task: {task.get('description')}"
            llm_response = self._call_llm(prompt)
            
            # 2. Formulate Result
            result = {
                "status": "success",
                "task_id": task_id,
                "output": llm_response,
                "agent": self.config.get("name"),
                "timestamp": time.time()
            }
            
            # 3. Publish Result to Bus
            output_channel = self.config.get("redis_config", {}).get("channels", {}).get("output", "agent:strategist:output")
            self.publish_message(output_channel, result)
            
            logger.info("Task execution completed successfully.")
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            self.state = "READY"

    def terminate(self):
        """
        Lifecycle method: Clean up and shutdown.
        """
        logger.info("Terminating agent...")
        self.state = "TERMINATED"
        # Cleanup logic here
        logger.info("Agent terminated.")

def main():
    parser = argparse.ArgumentParser(description="Run the Project Strategist Agent")
    parser.add_argument("--agent", type=str, help="Agent type (validation flag)", required=False)
    parser.add_argument("--task", type=str, help="JSON string task description", required=False)
    args = parser.parse_args()

    if args.agent and args.agent != "business":
        print(f"Invalid agent type '{args.agent}'. Expected 'business'.")
        sys.exit(1)

    try:
        agent = ProjectStrategistAgent()
        
        if args.task:
            try:
                task_payload = json.loads(args.task)
                result = agent.execute(task_payload)
                print(json.dumps(result, indent=2))
            except json.JSONDecodeError:
                logger.error("Invalid JSON provided for task")
                print("Error: Invalid JSON task string")
        else:
            # Default behavior if run without task (e.g. keep alive or run demo)
            logger.info("Running in standby mode (no task provided via CLI)")
            print(f"{agent.config.get('name')} is online and ready.")

    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
