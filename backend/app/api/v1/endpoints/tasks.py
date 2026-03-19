from typing import Any, List

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import models
from app.schemas import schemas
from app.api import deps

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
    query = db.query(models.Task).join(models.Project, models.Task.project_id == models.Project.id)
    if not current_user.is_superuser:
        query = query.filter(models.Project.owner_id == current_user.id)
    tasks = query.offset(skip).limit(limit).all()
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
    task_data = task_in.dict()
    # Remove 'type' from task_data before creating DB model if it exists
    task_type = task_data.pop("type", "general")

    project = db.query(models.Project).filter(models.Project.id == task_in.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not current_user.is_superuser and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough privileges")

    task = models.Task(
        **task_data,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    from app.services import broski_service
    broski_service.award_coins(current_user.id, 2, "Task created", db)

    # Push to Celery Task Queue
    queue_payload = {
        "id": task.id,
        "title": task.title,
        "type": task_type, # Use the type from input
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

@router.get("/{id}", response_model=schemas.Task)
def read_task(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task by ID.
    """
    query = db.query(models.Task).join(models.Project, models.Task.project_id == models.Project.id).filter(models.Task.id == id)
    if not current_user.is_superuser:
        query = query.filter(models.Project.owner_id == current_user.id)
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{id}", response_model=schemas.Task)
def update_task(
    *,
    db: Session = Depends(get_db),
    id: int,
    task_in: schemas.TaskUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    task_data = task_in.dict(exclude_unset=True)
    query = db.query(models.Task).join(models.Project, models.Task.project_id == models.Project.id).filter(models.Task.id == id)
    if not current_user.is_superuser:
        query = query.filter(models.Project.owner_id == current_user.id)
    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    old_status = task.status

    if "project_id" in task_data and task_data["project_id"] != task.project_id:
        project = db.query(models.Project).filter(models.Project.id == task_data["project_id"]).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not current_user.is_superuser and project.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough privileges")

    for key, value in task_data.items():
        setattr(task, key, value)

    db.add(task)
    db.commit()
    db.refresh(task)

    if "status" in task_data and old_status != models.TaskStatus.DONE and task.status == models.TaskStatus.DONE:
        from app.services import broski_service
        broski_service.award_coins(current_user.id, 10, "Task completed", db)
        broski_service.award_xp(current_user.id, 25, "Task completed", db)
        wallet = broski_service.get_wallet(current_user.id, db)
        today = datetime.now(timezone.utc).date()
        last = wallet.last_first_task_date.astimezone(timezone.utc).date() if wallet.last_first_task_date else None
        if last is None or last < today:
            broski_service.award_xp(current_user.id, 15, "First task of the day bonus!", db)
            wallet.last_first_task_date = datetime.now(timezone.utc)
            db.commit()

    return task
