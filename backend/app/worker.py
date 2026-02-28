from celery import Task
from app.core.celery_app import celery_app
from app.core.config import settings
from app.agents.router import router
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
    Receives a task payload and routes it to the appropriate agent via the AgentRouter.
    """
    task_id = task_payload.get("id")
    title = task_payload.get("title")
    description = task_payload.get("description") or title
    # Determine task type (could be passed in payload, defaulting to 'general')
    task_type = task_payload.get("type", "general") 
    
    logger.info(f"[INFO] Received task: hypercode.tasks.process_agent_job[{task_id}]")
    logger.info(f"[INFO] Orchestrator: Routing '{title}' (Type: {task_type})...")
    
    try:
        # Run the Router asynchronously
        plan = asyncio.run(router.route_task(task_type, description))
        
        logger.info(f"[INFO] Agent Output Preview: {plan[:100]}...")

        # 📝 THE NEW UPGRADE: Save the art to a file!
        import os
        output_dir = "/app/outputs" # Docker path
        os.makedirs(output_dir, exist_ok=True)
        
        # Now it saves as translation_21.md, pulse_22.md, research_23.md!
        file_path = f"{output_dir}/{task_type}_{task_id}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# 🧠 HyperCode Output: {task_type.upper()}\n\n")
            f.write(plan)
            
        logger.info(f"✅ Art saved to {file_path}")
        
        return {
            "status": "success", 
            "message": f"Task {task_id} processed",
            "agent": "Agent Swarm",
            "result": plan
        }
    except Exception as e:
        logger.error(f"[ERROR] Task processing failed: {e}")
        return {"status": "failed", "error": str(e)}
