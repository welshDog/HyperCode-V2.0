"""
Memory Agent — HyperCode V2.0
Minimal stub: key/value memory store backed by Redis, with PostgreSQL persistence.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Optional

import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memory-agent")

app = FastAPI(title="HyperCode Memory Agent", version="0.1.0")

_start_time = time.time()
_redis: Optional[aioredis.Redis] = None

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
PORT = int(os.getenv("PORT", "8082"))


@app.on_event("startup")
async def startup() -> None:
    global _redis
    try:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        await _redis.ping()
        logger.info("Memory Agent connected to Redis at %s", REDIS_URL)
    except Exception as exc:
        logger.warning("Redis not available at startup: %s", exc)
        _redis = None


@app.on_event("shutdown")
async def shutdown() -> None:
    if _redis:
        await _redis.aclose()


# ── Models ───────────────────────────────────────────────────────────────────

class MemoryEntry(BaseModel):
    key: str
    value: Any
    ttl: Optional[int] = None  # seconds; None = persist forever


class MemoryResponse(BaseModel):
    key: str
    value: Any
    found: bool


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict:
    redis_ok = False
    if _redis:
        try:
            await _redis.ping()
            redis_ok = True
        except Exception:
            pass
    return {
        "status": "ok",
        "agent": "memory-agent",
        "uptime_seconds": round(time.time() - _start_time, 1),
        "redis": "connected" if redis_ok else "disconnected",
    }


@app.get("/info")
async def info() -> dict:
    return {
        "name": "memory-agent",
        "version": "0.1.0",
        "port": PORT,
        "description": "Shared key/value memory store for HyperCode agents",
    }


@app.post("/memory", response_model=MemoryResponse)
async def store(entry: MemoryEntry) -> MemoryResponse:
    if not _redis:
        raise HTTPException(status_code=503, detail="Redis not available")
    ns_key = f"memory:{entry.key}"
    import json
    raw = json.dumps(entry.value)
    if entry.ttl:
        await _redis.setex(ns_key, entry.ttl, raw)
    else:
        await _redis.set(ns_key, raw)
    return MemoryResponse(key=entry.key, value=entry.value, found=True)


@app.get("/memory/{key}", response_model=MemoryResponse)
async def retrieve(key: str) -> MemoryResponse:
    if not _redis:
        raise HTTPException(status_code=503, detail="Redis not available")
    import json
    raw = await _redis.get(f"memory:{key}")
    if raw is None:
        return MemoryResponse(key=key, value=None, found=False)
    return MemoryResponse(key=key, value=json.loads(raw), found=True)


@app.delete("/memory/{key}")
async def forget(key: str) -> dict:
    if not _redis:
        raise HTTPException(status_code=503, detail="Redis not available")
    deleted = await _redis.delete(f"memory:{key}")
    return {"key": key, "deleted": bool(deleted)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, log_level="info")
