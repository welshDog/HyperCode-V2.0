"""
🚀 MAPE-K Bootstrap — Wire the engine into the Healer Agent on startup.

Add this to agents/healer/main.py startup:

    from mape_k_bootstrap import start_mape_k
    @app.on_event("startup")
    async def startup():
        await start_mape_k(app)
"""

import asyncio
import logging
from fastapi import FastAPI
from .mape_k_engine import KnowledgeBase, mape_k_loop, DEFAULT_SERVICES
from .mape_k_api import router as mape_k_router, set_knowledge_base

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
