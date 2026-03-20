from pydantic import BaseModel
from typing import Optional, List

class ContainerStatus(BaseModel):
    name: str
    status: str  # running, exited, dead, etc.
    health: str  # healthy, unhealthy, starting, none
    started_at: Optional[str] = None
    restart_count: int = 0

class HealResult(BaseModel):
    agent: str
    status: str
    action: str
    details: Optional[str] = None
    timestamp: str

class HealRequest(BaseModel):
    agents: Optional[List[str]] = None
    force: bool = False
    retry_attempts: int = 2
    timeout_seconds: int = 5
