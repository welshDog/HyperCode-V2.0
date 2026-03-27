"""
🚀 MAPE-K Bootstrap — Wire the engine into the Healer Agent on startup.

Usage in agents/healer/main.py lifespan:

    from mape_k_bootstrap import start_mape_k
    kb = await start_mape_k(app)
"""
import asyncio
import logging
import sys
import os

# 📍 Add /app/healer to sys.path so absolute imports work inside Docker
# The Dockerfile COPYs healer/ to /app/healer and sets WORKDIR /app
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from fastapi import FastAPI
from mape_k_engine import KnowledgeBase, mape_k_loop, DEFAULT_SERVICES
from mape_k_api import router as mape_k_router, set_knowledge_base

logger = logging.getLogger("mape_k_bootstrap")


async def start_mape_k(app: FastAPI, interval: int = 10):
    """
    Bootstrap the MAPE-K engine:
    1. Create shared KnowledgeBase
    2. Register API router
    3. Start background MAPE-K loop
    """
    kb = KnowledgeBase()
    set_knowledge_base(kb)

    # Mount MAPE-K API endpoints
    app.include_router(mape_k_router)
    logger.info("✅ MAPE-K API routes registered at /mape-k/*")

    # Start the loop as a background task
    asyncio.create_task(
        mape_k_loop(
            services=DEFAULT_SERVICES,
            kb=kb,
            interval_seconds=interval,
        )
    )
    logger.info(f"🧠 MAPE-K loop started — polling every {interval}s")
    return kb
