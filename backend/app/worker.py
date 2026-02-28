from celery import Task
from app.core.celery_app import celery_app
from app.core.config import settings
from app.agents.brain import brain
import logging
import asyncio
import json

logger = logging.getLogger(__name__)

class AgentTask(Task):
    """
    Base class for agent tasks that handles errors and logging.
    """
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed: {exc}")

@celery_app.task(base=AgentTask, name="hypercode.tasks.process_agent_job")
def process_agent_job(task_payload: dict):
    """
    The main entry point for the Orchestrator.
    Receives a task payload and routes it to the appropriate agent.
    """
    task_id = task_payload.get("id")
    title = task_payload.get("title")
    description = task_payload.get("description") or title
    
    logger.info(f"[INFO] Received task: hypercode.tasks.process_agent_job[{task_id}]")
    logger.info(f"[INFO] Orchestrator: Assigning '{title}' to Backend Specialist...")
    
    try:
        # Run the Brain asynchronously
        logger.info(f"[INFO] Orchestrator: Invoking the Brain (Claude 3.5 Sonnet)...")
        plan = asyncio.run(brain.think("Backend Specialist", description))
        
        logger.info(f"[INFO] Brain Output Preview: {plan[:100]}...")
        
        return {
            "status": "success", 
            "message": f"Task {task_id} processed",
            "agent": "Backend Specialist",
            "result": plan
        }
    except Exception as e:
        logger.error(f"[ERROR] Task processing failed: {e}")
        return {"status": "failed", "error": str(e)}
