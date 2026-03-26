"""
📡 MAPE-K API — Expose healing status + stats over HTTP
Mounts onto the existing Healer Agent FastAPI app.
"""

from fastapi import APIRouter
from datetime import datetime, timezone
from .mape_k_engine import KnowledgeBase, HealAction

router = APIRouter(prefix="/mape-k", tags=["MAPE-K Self-Healing"])

# Injected at startup — set this in main.py
_kb: KnowledgeBase | None = None


def set_knowledge_base(kb: KnowledgeBase):
    global _kb
    _kb = kb


@router.get("/status")
async def get_mape_k_status():
    """🧠 Current MAPE-K engine health + anomaly scores."""
    if not _kb:
        return {"error": "MAPE-K engine not initialised"}
    return {
        "engine": "MAPE-K v1.0 — HyperCode Self-Healing Brain",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "stats": _kb.stats(),
        "anomaly_scores": _kb.anomaly_scores,
        "action_success_rates": {
            action.value: round(sum(results) / len(results) * 100, 1)
            for action, results in _kb.action_success_rates.items()
            if results
        },
    }


@router.get("/history")
async def get_heal_history(limit: int = 20):
    """📋 Recent healing events — what broke + what was done."""
    if not _kb:
        return {"error": "MAPE-K engine not initialised"}
    events = _kb.heal_history[-limit:]
    return {
        "total_events": len(_kb.heal_history),
        "showing": len(events),
        "events": [
            {
                "timestamp": e.timestamp,
                "service": e.service,
                "status_before": e.status_before.value if e.status_before else None,
                "action": e.action_taken.value,
                "success": e.success,
                "reason": e.reason,
                "mttr_seconds": e.mttr_seconds,
            }
            for e in reversed(events)
        ],
    }


@router.get("/metrics")
async def get_metrics():
    """📊 Key MAPE-K performance metrics for Grafana/dashboards."""
    if not _kb:
        return {"error": "MAPE-K engine not initialised"}
    stats = _kb.stats()
    return {
        "mape_k_total_heals": stats["total_heals"],
        "mape_k_heals_last_hour": stats["heals_last_hour"],
        "mape_k_auto_fix_success_rate_pct": stats["auto_fix_success_rate"],
        "mape_k_avg_mttr_seconds": stats["avg_mttr_seconds"],
        "mape_k_uptime_seconds": stats["uptime_seconds"],
        "mape_k_anomaly_scores": _kb.anomaly_scores,
    }
