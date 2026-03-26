"""
HyperHealth Pydantic + SQLAlchemy models
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, AnyHttpUrl, Field

# ---------------------------------------------------------------------------
# Enums / types
# ---------------------------------------------------------------------------
CheckType = Literal[
    "cpu", "memory", "disk", "network",
    "http", "db", "queue", "cache",
    "tls", "vuln_scan", "compliance",
]

CheckStatus = Literal["OK", "WARN", "CRIT", "UNKNOWN"]

Severity = Literal["info", "warn", "crit"]


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
class Thresholds(BaseModel):
    warn: float
    crit: float
    window_seconds: int = 60


# ---------------------------------------------------------------------------
# CheckDefinition
# ---------------------------------------------------------------------------
class CheckDefinitionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    type: CheckType
    target: str = Field(..., description="URL, DSN, host:port, queue name, etc.")
    environment: str = Field(default="prod", description="blue, green, prod, staging")
    interval_seconds: int = Field(default=30, ge=5, le=3600)
    thresholds: Dict[str, Thresholds] = Field(
        default_factory=lambda: {"latency_ms": Thresholds(warn=500, crit=2000)}
    )
    alert_policy_id: Optional[int] = None
    self_heal_policy_id: Optional[int] = None
    tags: List[str] = []


class CheckDefinitionOut(BaseModel):
    id: UUID
    name: str
    type: str
    target: str
    environment: str
    interval_seconds: int
    enabled: bool
    tags: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# CheckResult
# ---------------------------------------------------------------------------
class CheckResultOut(BaseModel):
    id: UUID
    check_id: UUID
    status: CheckStatus
    latency_ms: Optional[float]
    value: Optional[float]
    message: Optional[str]
    environment: str
    started_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Incident
# ---------------------------------------------------------------------------
class IncidentOut(BaseModel):
    id: UUID
    check_id: Optional[UUID]
    title: str
    summary: str
    severity: Severity
    environment: str
    service: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Health Report
# ---------------------------------------------------------------------------
class HealthReport(BaseModel):
    environment: str
    overall_status: CheckStatus
    total_checks: int
    critical_count: int
    warning_count: int
    ok_count: int
    open_incidents: List[Any] = []
    generated_at: str


# ---------------------------------------------------------------------------
# Self-Heal Policy
# ---------------------------------------------------------------------------
class SelfHealPolicyCreate(BaseModel):
    name: str
    enabled: bool = True
    trigger_status: CheckStatus = "CRIT"
    trigger_count: int = Field(default=3, description="Failures before triggering")
    trigger_window_seconds: int = 120
    action: Literal[
        "restart_container",
        "call_healer",
        "rollback_deployment",
        "purge_cache",
        "resync_queue",
    ]
    action_params: Dict[str, Any] = {}
    max_retries_per_hour: int = 3
    require_human_approval: bool = False
