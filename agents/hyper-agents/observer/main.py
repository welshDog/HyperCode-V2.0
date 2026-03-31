"""
HyperCode V2.0 — ObserverAgent Container Entrypoint
====================================================
Exposes the ObserverAgent over HTTP with metric recording,
alert rule management, and real-time stats endpoints.

Port  : 8092 (configurable via AGENT_PORT env)
Health: GET /health
"""

from __future__ import annotations

import os
from typing import Any, List, Optional

import uvicorn
from fastapi import HTTPException
from pydantic import BaseModel

from src.agents.hyper_agents import AgentArchetype
from src.agents.hyper_agents.observer import (
    Alert,
    AlertRule,
    AlertSeverity,
    Metric,
    MetricType,
    ObserverAgent,
)

# ── Config ────────────────────────────────────────────────────────────────────
AGENT_NAME = os.getenv("AGENT_NAME", "sys-observer-01")
AGENT_PORT = int(os.getenv("AGENT_PORT", "8092"))
CREW_URL = os.getenv("CREW_ORCHESTRATOR_URL", "http://crew-orchestrator:8081")
WINDOW_SIZE = int(os.getenv("OBSERVER_WINDOW_SIZE", "200"))


# ── Concrete agent implementation ─────────────────────────────────────────────

class HyperObserverAgent(ObserverAgent):
    """Deployed ObserverAgent — routes task dicts to metric/alert methods."""

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        action = task.get("action", "stats")

        if action == "record":
            metric = Metric(
                name=task["name"],
                value=float(task["value"]),
                metric_type=MetricType(task.get("metric_type", "gauge")),
                tags=task.get("tags", {}),
                unit=task.get("unit", ""),
            )
            self.record(metric)
            return {"status": "recorded", "metric": metric.label, "value": metric.value}

        if action == "record_many":
            metrics = [
                Metric(name=m["name"], value=float(m["value"]))
                for m in task.get("metrics", [])
            ]
            self.record_many(metrics)
            return {"status": "recorded", "count": len(metrics)}

        if action == "stats":
            return self.stats

        if action == "alerts":
            return {
                "active_alerts": [
                    {"id": a.alert_id, "severity": a.severity.value, "summary": a.summary}
                    for a in self.get_active_alerts()
                ]
            }

        return {"status": "ok", "stats": self.stats}


# ── Alert inbox — callbacks write here, GET /alerts reads it ──────────────────

_fired_alerts: list[dict[str, Any]] = []


def _alert_callback(alert: Alert) -> None:
    _fired_alerts.append({
        "alert_id": alert.alert_id,
        "severity": alert.severity.value,
        "metric_name": alert.metric_name,
        "current_value": alert.current_value,
        "threshold": alert.threshold,
        "message": alert.message,
        "what_to_do": alert.what_to_do,
        "timestamp": alert.timestamp,
    })


# ── Instantiate ───────────────────────────────────────────────────────────────

agent = HyperObserverAgent(
    name=AGENT_NAME,
    archetype=AgentArchetype.OBSERVER,
    port=AGENT_PORT,
    window_size=WINDOW_SIZE,
    alert_callback=_alert_callback,
)
app = agent.app


# ── Request models ────────────────────────────────────────────────────────────

class MetricRequest(BaseModel):
    name: str
    value: float
    metric_type: str = "gauge"
    tags: dict[str, str] = {}
    unit: str = ""


class MetricBatchRequest(BaseModel):
    metrics: List[MetricRequest]


class AlertRuleRequest(BaseModel):
    name: str
    metric_name: str
    threshold: float
    severity: str  # info | warning | critical
    message_template: str
    what_to_do: str
    comparison: str = "gt"  # gt | lt | eq | gte | lte
    cooldown_seconds: float = 60.0


class EventRequest(BaseModel):
    event_type: str
    data: dict[str, Any] = {}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/execute")
async def execute(task: dict[str, Any]) -> dict[str, Any]:
    """General-purpose task execution gateway."""
    return await agent.execute(task)


@app.post("/metrics", status_code=201)
async def record_metric(req: MetricRequest) -> dict[str, Any]:
    """Record a single metric observation."""
    metric = Metric(
        name=req.name,
        value=req.value,
        metric_type=MetricType(req.metric_type),
        tags=req.tags,
        unit=req.unit,
    )
    agent.record(metric)
    return {"status": "recorded", "metric": metric.label, "value": metric.value}


@app.post("/metrics/batch", status_code=201)
async def record_metrics_batch(req: MetricBatchRequest) -> dict[str, Any]:
    """Record multiple metrics at once."""
    metrics = [
        Metric(name=m.name, value=m.value, metric_type=MetricType(m.metric_type), tags=m.tags, unit=m.unit)
        for m in req.metrics
    ]
    agent.record_many(metrics)
    return {"status": "recorded", "count": len(metrics)}


@app.get("/metrics/{metric_name}/stats")
async def metric_stats(metric_name: str) -> dict[str, Any]:
    """Return min/max/avg/latest/count for a tracked metric."""
    stats = agent.get_metric_stats(metric_name)
    if not stats:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found.")
    return {"metric": metric_name, **stats}


@app.get("/metrics/{metric_name}/rate")
async def metric_rate(metric_name: str, window_seconds: float = 60.0) -> dict[str, Any]:
    """Return the rate-of-change for a metric over a rolling window."""
    rate = agent.get_rate(metric_name, window_seconds=window_seconds)
    return {"metric": metric_name, "rate_per_second": rate, "window_seconds": window_seconds}


@app.post("/rules", status_code=201)
async def add_alert_rule(req: AlertRuleRequest) -> dict[str, Any]:
    """Register a new threshold alerting rule."""
    try:
        severity = AlertSeverity(req.severity)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unknown severity: {req.severity}. Use: info, warning, critical")
    rule = AlertRule(
        name=req.name,
        metric_name=req.metric_name,
        threshold=req.threshold,
        severity=severity,
        message_template=req.message_template,
        what_to_do=req.what_to_do,
        comparison=req.comparison,
        cooldown_seconds=req.cooldown_seconds,
    )
    agent.add_alert_rule(rule)
    return {"status": "rule_added", "rule_name": req.name}


@app.get("/alerts")
async def get_active_alerts() -> dict[str, Any]:
    """Return all currently active (unresolved) alerts."""
    return {
        "active_alerts": [
            {
                "alert_id": a.alert_id,
                "severity": a.severity.value,
                "metric_name": a.metric_name,
                "current_value": a.current_value,
                "threshold": a.threshold,
                "summary": a.summary,
                "what_to_do": a.what_to_do,
            }
            for a in agent.get_active_alerts()
        ]
    }


@app.get("/alerts/history")
async def alert_history() -> dict[str, Any]:
    """Return all fired alerts (including resolved)."""
    return {"alerts": _fired_alerts}


@app.post("/events", status_code=201)
async def log_event(req: EventRequest) -> dict[str, Any]:
    """Record a structured event to the observer's event log."""
    agent.log_event(req.event_type, req.data)
    return {"status": "logged", "event_type": req.event_type}


@app.get("/stats")
async def stats() -> dict[str, Any]:
    """Current observer statistics."""
    return agent.stats


# ── Lifecycle ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup() -> None:
    await agent.initialize()
    agent.register_with_crew(crew_url=CREW_URL)


@app.on_event("shutdown")
async def shutdown() -> None:
    agent.shutdown()


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=AGENT_PORT, log_level="info")
