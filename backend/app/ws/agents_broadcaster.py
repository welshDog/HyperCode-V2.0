"""
backend/app/ws/agents_broadcaster.py

Real-time WebSocket broadcaster for agent statuses.

AgentStatus is the canonical Pydantic model for a single agent heartbeat.
The /ws/agents handler calls _get_agent_statuses() and serialises the list
through this model, so any new fields added here are automatically included
in every broadcast — no changes needed in the handler itself.
"""
from __future__ import annotations

import json
import asyncio
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

try:
    import redis.asyncio as aioredis  # redis-py >= 4.2
except ImportError:  # pragma: no cover
    import aioredis  # fallback for older installs


# ---------------------------------------------------------------------------
# Pydantic model
# ---------------------------------------------------------------------------

class AgentStatus(BaseModel):
    """Single-agent status payload broadcast over /ws/agents."""

    id:           str
    name:         str
    status:       str
    last_seen:    str  | None = None
    last_action:  str  | None = None
    coins:        int         = 0

    # XP / progression fields — agents write these to their Redis heartbeat
    # hash when available; we return safe defaults when not present.
    xp:           int         = 0
    level:        int         = 1
    xp_to_next:   int         = 100


# ---------------------------------------------------------------------------
# Redis heartbeat reader
# ---------------------------------------------------------------------------

async def _get_agent_statuses(redis: Any) -> list[AgentStatus]:
    """
    Scan all agent:heartbeat:* keys in Redis and build AgentStatus objects.

    XP fields are optional in the heartbeat hash — missing keys fall back to
    the Pydantic defaults (xp=0, level=1, xp_to_next=100).
    """
    statuses: list[AgentStatus] = []

    async for key in redis.scan_iter("agent:heartbeat:*"):
        hb: dict[str, str] = await redis.hgetall(key)
        if not hb:
            continue

        # Decode bytes keys/values if redis-py returns bytes
        hb = {
            (k.decode() if isinstance(k, bytes) else k):
            (v.decode() if isinstance(v, bytes) else v)
            for k, v in hb.items()
        }

        statuses.append(
            AgentStatus(
                id          = hb.get("id",          key),
                name        = hb.get("name",        "unknown"),
                status      = hb.get("status",      "unknown"),
                last_seen   = hb.get("last_seen"),
                last_action = hb.get("last_action"),
                coins       = int(hb.get("coins",   0)),
                # XP progression — safe defaults when agent hasn't written them yet
                xp          = int(hb.get("xp",         0)),
                level       = int(hb.get("level",       1)),
                xp_to_next  = int(hb.get("xp_to_next", 100)),
            )
        )

    return statuses


# ---------------------------------------------------------------------------
# WebSocket handler  (/ws/agents)
# ---------------------------------------------------------------------------

REFRESH_INTERVAL = 2  # seconds between broadcasts


async def ws_agents_handler(websocket: WebSocket, redis: Any) -> None:
    """
    Accepts the WebSocket connection and streams agent statuses every
    REFRESH_INTERVAL seconds until the client disconnects.

    Data path:
        Redis heartbeat hashes
          -> _get_agent_statuses()     (reads + maps to AgentStatus)
          -> AgentStatus.model_dump()  (serialises, includes xp/level/xp_to_next)
          -> JSON over WS

    Because the handler only ever calls _get_agent_statuses(), any fields
    added to AgentStatus / _get_agent_statuses() are automatically included
    in every broadcast without touching this function.
    """
    await websocket.accept()
    try:
        while True:
            statuses = await _get_agent_statuses(redis)
            payload  = [s.model_dump() for s in statuses]
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(REFRESH_INTERVAL)
    except WebSocketDisconnect:
        pass
