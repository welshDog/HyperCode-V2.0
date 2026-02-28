from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import models
from app.schemas import schemas
from app.api import deps
# Removed: from app.core.queue import push_task_to_queue

router = APIRouter()

@router.get("/", response_model=List[schemas.Task])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve tasks.
    """
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return tasks

@router.post("/", response_model=schemas.Task)
def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new task.
    """
    task = models.Task(
        **task_in.dict(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Push to Celery Task Queue
    queue_payload = {
        "id": task.id,
        "title": task.title,
        "type": "code_generation", # Defaulting for now
        "description": task.description or task.title,
        "priority": task.priority,
        "status": "pending",
        "project_id": task.project_id
    }
    
    # Fire and forget (or handle error)
    # Import inside function to avoid circular imports if any
    from app.core.celery_app import celery_app
    celery_app.send_task("hypercode.tasks.process_agent_job", args=[queue_payload])

    return task
