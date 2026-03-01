from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# --- ENUMS ---
class UserRole(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[UserRole] = UserRole.DEVELOPER

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

# --- PROJECT SCHEMAS ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[ProjectStatus] = ProjectStatus.DRAFT

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- TASK SCHEMAS ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    output: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[str] = "medium"

class TaskCreate(TaskBase):
    project_id: int
    assignee_id: Optional[int] = None
    type: Optional[str] = "general"

class TaskUpdate(TaskBase):
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None

class Task(TaskBase):
    id: int
    project_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- AUTH SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None
