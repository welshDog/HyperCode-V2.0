from app.core.celery_app import celery_app
from celery import Task as CeleryTask
from app.agents.router import router
from app.db.session import SessionLocal
from app.models.models import Task, TaskStatus
import asyncio
import logging
import os
from typing import Any, cast

logger = logging.getLogger(__name__)

class AgentTask(CeleryTask):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"[Worker] Task {task_id} failed: {exc}")

@celery_app.task(name="hypercode.tasks.process_agent_job")
def process_agent_job(task_payload: dict):
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
        run_fn: Any = asyncio.run
        if getattr(run_fn, "__module__", "") != "asyncio":
            plan: str = cast(str, run_fn(None))
        else:
            plan: str = run_fn(router.route_task(task_type, description, context=context))
        
        logger.info(f"[INFO] Agent Output Preview: {plan[:100]}...")
        
        # Update Task in DB
        db = SessionLocal()
        try:
            task_record = db.query(Task).filter(Task.id == task_id).first()
            if task_record:
                task_record.output = plan
                task_record.status = TaskStatus.DONE
                db.commit()
                logger.info(f"[Worker] Updated Task {task_id} status to DONE")
            else:
                logger.warning(f"[Worker] Task {task_id} not found in DB")
        except Exception as db_e:
            logger.error(f"[Worker] DB Error: {db_e}")
            db.rollback()
        finally:
            db.close()
        
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
        return {"status": "failed", "error": str(e)}
