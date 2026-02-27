"""
HyperCode Deployment Tool
Provides Docker control capabilities for the DevOps agent.
"""
import subprocess
import logging
import os
from typing import Dict, Any

logger = logging.getLogger("deployer")

class Deployer:
    """Handles container management and deployment tasks"""
    
    @staticmethod
    def list_containers() -> str:
        """Returns list of running containers"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "table {{.ID}}\t{{.Names}}\t{{.Status}}"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error listing containers: {e.stderr}"

    @staticmethod
    def deploy_service(service_name: str) -> Dict[str, Any]:
        """
        Rebuilds and restarts a specific service.
        """
        logger.info(f"Initiating deployment for {service_name}")
        
        try:
            # 1. Build
            logger.info("Building...")
            build_res = subprocess.run(
                ["docker", "compose", "build", service_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 2. Up (Rolling update)
            logger.info("Restarting...")
            up_res = subprocess.run(
                ["docker", "compose", "up", "-d", "--no-deps", service_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                "status": "success",
                "message": f"Deployed {service_name}",
                "build_log": build_res.stdout,
                "deploy_log": up_res.stdout
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Deployment failed: {e.stderr}")
            return {
                "status": "error",
                "message": f"Deployment failed: {e.stderr}",
                "exit_code": e.returncode
            }
            
    @staticmethod
    def get_service_logs(service_name: str, lines: int = 50) -> str:
        """Fetch recent logs for validation"""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), service_name],
                capture_output=True,
                text=True
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error fetching logs: {str(e)}"
