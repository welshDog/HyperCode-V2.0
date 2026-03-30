from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, projects, tasks, dashboard, memory, orchestrator, broski, planning

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(dashboard.router, prefix="", tags=["dashboard_compat"])  # /execute and /logs compat
api_router.include_router(orchestrator.router, prefix="/orchestrator", tags=["orchestrator"])
api_router.include_router(broski.router, prefix="/broski", tags=["broski"])  # 🔥 BROski$ Token System
api_router.include_router(planning.router, prefix="/planning", tags=["planning"])  # 🗺️ Planning System
