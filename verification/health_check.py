import requests
import sys
import os
import subprocess
import json
import time
import logging
from datetime import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("health_check.log")
    ]
)
logger = logging.getLogger(__name__)

# Configuration
MAX_RETRIES = 3
RETRY_DELAY = 5

SERVICES = {
    "hypercode-core": {"url": "http://localhost:8000/health", "port": 8000, "critical": True},
    "broski-terminal": {"url": "http://localhost:3000/api/health", "port": 3000, "critical": True},
    "hyperflow-editor": {"url": "http://localhost:5173/", "port": 5173, "critical": False},
    "coder-agent": {"url": "http://localhost:8001/health", "port": 8001, "critical": True},
    "crew-orchestrator": {"url": "http://localhost:8080/health", "port": 8080, "critical": True},
    "hypercode-dashboard": {"url": "http://localhost:8088/", "port": 8088, "critical": False},
    "grafana": {"url": "http://localhost:3001/api/health", "port": 3001, "critical": False},
    "prometheus": {"url": "http://localhost:9090/-/healthy", "port": 9090, "critical": False},
}

# Categorize containers for reporting
AGENTS = [
    "coder-agent",
    "frontend-specialist",
    "backend-specialist",
    "database-architect",
    "qa-engineer",
    "devops-engineer",
    "security-engineer",
    "system-architect",
    "project-strategist"
]

INFRASTRUCTURE = [
    "hypercode-core",
    "broski-terminal",
    "hyperflow-editor",
    "crew-orchestrator",
    "celery-worker",
    "redis",
    "postgres",
    "hypercode-dashboard",
    "grafana",
    "prometheus",
    "jaeger",
    "hypercode-ollama"
]

def check_http_service(name, url):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True, f"UP ({response.status_code})"
            else:
                logger.warning(f"{name}: Received status {response.status_code} (Attempt {attempt + 1}/{MAX_RETRIES})")
        except Exception as e:
            logger.warning(f"{name}: Connection failed - {str(e)} (Attempt {attempt + 1}/{MAX_RETRIES})")
        
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)
            
    return False, "DOWN (Max retries exceeded)"

def check_docker_health(container_name):
    for attempt in range(MAX_RETRIES):
        try:
            # Check health status first
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name],
                capture_output=True, text=True
            )
            
            status = result.stdout.strip()
            
            # If no healthcheck defined, check running state
            if not status or "Template parsing error" in status:
                 result = subprocess.run(
                     ["docker", "inspect", "--format", "{{.State.Status}}", container_name],
                     capture_output=True, text=True
                 )
                 status = result.stdout.strip()

            if status in ["healthy", "running"]:
                return True, status
            
            logger.warning(f"{container_name}: Status '{status}' (Attempt {attempt + 1}/{MAX_RETRIES})")
            
        except Exception as e:
            logger.error(f"{container_name}: Docker check failed - {str(e)}")
            
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)

    return False, status if 'status' in locals() else "UNKNOWN"

def main():
    logger.info("Starting HyperCode System Health Check")
    logger.info("======================================")
    
    overall_status = True
    
    # 1. Check Agent Swarm
    logger.info("\n[AGENT SWARM STATUS]")
    logger.info(f"{'Agent':<25} | {'Status':<15}")
    logger.info("-" * 45)
    
    agent_health_count = 0
    for agent in AGENTS:
        is_healthy, status = check_docker_health(agent)
        icon = "[OK]" if is_healthy else "[FAIL]"
        logger.info(f"{icon} {agent:<23} | {status}")
        if is_healthy:
            agent_health_count += 1
        else:
            overall_status = False

    swarm_status = "OPERATIONAL" if agent_health_count == len(AGENTS) else "DEGRADED"
    logger.info(f"Summary: {agent_health_count}/{len(AGENTS)} Agents Active - Swarm Status: {swarm_status}")

    # 2. Check Infrastructure
    logger.info("\n[INFRASTRUCTURE STATUS]")
    logger.info(f"{'Container':<25} | {'Status':<15}")
    logger.info("-" * 45)
    
    for container in INFRASTRUCTURE:
        is_healthy, status = check_docker_health(container)
        icon = "[OK]" if is_healthy else "[FAIL]"
        logger.info(f"{icon} {container:<23} | {status}")
        if not is_healthy:
            overall_status = False

    # 3. Check Public Endpoints
    logger.info("\n[PUBLIC ENDPOINTS]")
    logger.info(f"{'Service':<25} | {'Status':<30}")
    logger.info("-" * 60)

    for name, config in SERVICES.items():
        is_up, status = check_http_service(name, config["url"])
        icon = "[OK]" if is_up else "[FAIL]"
        logger.info(f"{icon} {name:<23} | {status}")
        if not is_up and config["critical"]:
            overall_status = False

    logger.info("\n" + "=" * 60)
    if overall_status:
        logger.info("SYSTEM STATUS: OPERATIONAL")
        sys.exit(0)
    else:
        logger.error("SYSTEM STATUS: ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()
