from app.core.celery_app import celery_app
from celery import Task
from app.agents.router import router
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

class AgentTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"[Worker] Task {task_id} failed: {exc}")

@celery_app.task(name="hypercode.tasks.process_agent_job", bind=True)
def process_agent_job(self, task_payload: dict):
    """
    Main worker entrypoint for processing agent tasks.
    """
    logger.info(f"[Worker] Received task: {task_payload}")
    
    task_id = task_payload.get("id")
    task_type = task_payload.get("type", "general")
    description = task_payload.get("description", "")
    output_dir = "/app/outputs" # Internal Docker path

    try:
        # Pass context with task_id to router
        context = {"task_id": task_id}
        
        # Run the Router asynchronously
        plan = asyncio.run(router.route_task(task_type, description, context=context))
        
        logger.info(f"[INFO] Agent Output Preview: {plan[:100]}...")
        
        # Save output to disk (Legacy/Backup)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        file_path = f"{output_dir}/{task_type}_{task_id}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# 🧠 HyperCode Output: {task_type.upper()}\n\n")
            f.write(plan)
            
        logger.info(f"[Worker] Saved output to {file_path}")
        
        return {"status": "completed", "output_file": file_path, "preview": plan[:200]}

    except Exception as e:
        logger.error(f"[Worker] Error processing task {task_id}: {e}")
        # self.retry(exc=e, countdown=60) # Optional retry
        return {"status": "failed", "error": str(e)}
