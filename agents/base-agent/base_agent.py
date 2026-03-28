"""
HyperCode V2.0 - Hyper Agents: Base Agent
==========================================
Foundation class for all new HyperCode agents.

Architecture: Additive extension of HyperCode V2.0.
Does NOT modify existing agents (Crew, Healer, Brain, Dashboard).

Usage:
    class MyWorkerAgent(HyperAgent):
        async def execute(self, task: dict) -> dict:
            ...

    # Remember: register_with_crew is async now
    # await agent.register_with_crew()

See docs/hyper-agents/README.md for full guide.
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AgentArchetype(str, Enum):
    """Supported agent archetypes for HyperCode V2.0."""

    WORKER = "worker"
    OBSERVER = "observer"
    ARCHITECT = "architect"
    HEALER_VARIANT = "healer_variant"
    CUSTOM = "custom"


class AgentStatus(str, Enum):
    """Agent lifecycle states."""

    STARTING = "starting"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    STOPPING = "stopping"


class AgentHealthResponse(BaseModel):
    """Standard health check response for all Hyper Agents."""

    name: str
    archetype: AgentArchetype
    status: AgentStatus
    version: str
    uptime_seconds: float
    message: str


class NDErrorResponse(BaseModel):
    """
    Neurodivergent-friendly error response.

    Always structured as: what happened > why it matters > what to do.
    No blame language. No cryptic codes as the first thing shown.
    """

    title: str
    what_happened: str
    why_it_matters: str
    options: list[str]
    error_code: str | None = None
    technical_detail: str | None = None


class HyperAgent(ABC):
    """
    Base class for all HyperCode V2.0 Hyper Agents.

    Provides:
    - Standard health endpoint
    - ND-friendly error formatting
    - Crew Orchestrator registration interface (async)
    - The Brain handshake interface (future extension)
    - BROski$ event hooks (Phase 2)

    All subclasses must implement `execute()`.

    NOTE:
        `register_with_crew()` is now asynchronous and must be awaited
        from an async context (or via `asyncio.run()` in scripts).
    """

    def __init__(
        self,
        name: str,
        archetype: AgentArchetype,
        version: str = "1.0.0",
        port: int = 8090,
    ) -> None:
        """Initialise a new Hyper Agent."""
        self.name = name
        self.archetype = archetype
        self.version = version
        self.port = port
        self.status = AgentStatus.STARTING
        self._start_time = time.time()
        self.app = FastAPI(
            title=f"HyperCode Agent: {name}",
            description=f"A {archetype.value} agent for HyperCode V2.0.",
            version=version,
        )
        self._register_base_routes()
        logger.info(f"[{self.name}] Initialised as {archetype.value} agent.")

    def _register_base_routes(self) -> None:
        """Register standard routes that all agents must expose."""

        @self.app.get("/health", response_model=AgentHealthResponse)
        async def health() -> AgentHealthResponse:
            """Standard health check. Required by Crew Orchestrator + Mission Control."""
            return AgentHealthResponse(
                name=self.name,
                archetype=self.archetype,
                status=self.status,
                version=self.version,
                uptime_seconds=round(time.time() - self._start_time, 2),
                message=f"{self.name} is {self.status.value}. All good.",
            )

        @self.app.get("/info")
        async def info() -> dict[str, Any]:
            """Agent metadata for Mission Control dashboard."""
            return {
                "name": self.name,
                "archetype": self.archetype.value,
                "version": self.version,
                "port": self.port,
                "status": self.status.value,
                "hypercode_version": "2.0",
            }

    @abstractmethod
    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Core task execution logic. Must be implemented by all agents.

        Args:
            task: Dict with task type, payload, and metadata.

        Returns:
            Dict with result, status, and message (always include 'message').
        """
        ...

    def format_nd_error(
        self,
        title: str,
        what_happened: str,
        why_it_matters: str,
        options: list[str],
        error_code: str | None = None,
        technical_detail: str | None = None,
    ) -> NDErrorResponse:
        """
        Format an error in a neurodivergent-friendly way.

        ALWAYS use this method for errors shown to users.
        Never return raw stack traces as the primary error.

        Args:
            title: Short, plain-English title (e.g. "Redis connection failed").
            what_happened: One sentence explaining what went wrong.
            why_it_matters: One sentence on the impact.
            options: List of concrete next steps the user can take.
            error_code: Optional internal error code (not shown first).
            technical_detail: Optional raw detail (shown last, collapsed).
        """
        return NDErrorResponse(
            title=title,
            what_happened=what_happened,
            why_it_matters=why_it_matters,
            options=options,
            error_code=error_code,
            technical_detail=technical_detail,
        )

    async def register_with_crew(
        self,
        crew_url: str = "http://localhost:8081",
    ) -> dict[str, Any]:
        """
        Register this agent with the Crew Orchestrator (ASYNC).

        This method performs an HTTP POST to the Crew service and is now fully
        asynchronous, using `httpx.AsyncClient` under the hood.

        Call this during startup. The Crew will then route tasks to this agent.

        Behaviour:
            - On success: returns the JSON body from the Crew response.
            - On failure: logs a warning and returns:
                {"status": "registration_pending", "error": "<stringified error>"}

        This preserves the original exception behaviour: no new exception types
        are raised from this method; errors are folded into the return dict.
        """
        import httpx  # lazy import to avoid circular deps

        payload: dict[str, Any] = {
            "name": self.name,
            "archetype": self.archetype.value,
            "version": self.version,
            "port": self.port,
            "health_url": f"http://localhost:{self.port}/health",
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{crew_url}/agents/register",
                    json=payload,
                )
                resp.raise_for_status()
            logger.info("[%s] Registered with Crew Orchestrator at %s", self.name, crew_url)
            data: Any = resp.json()
            return data  # type: ignore[no-any-return]
        except Exception as exc:  # noqa: BLE001 - broad to preserve original behaviour
            logger.warning("[%s] Crew registration failed: %s", self.name, exc)
            return {"status": "registration_pending", "error": str(exc)}

    def set_ready(self) -> None:
        """Mark agent as ready. Call after all startup tasks complete."""
        self.status = AgentStatus.READY
        logger.info("[%s] Status: READY", self.name)

    def set_busy(self) -> None:
        """Mark agent as busy during task execution."""
        self.status = AgentStatus.BUSY

    def set_error(self) -> None:
        """Mark agent as in error state."""
        self.status = AgentStatus.ERROR
        logger.error("[%s] Status: ERROR", self.name)


# ---------------------------------------------------------------------------
# Simple asyncio.run() demo
# ---------------------------------------------------------------------------


class _DemoAgent(HyperAgent):
    """Minimal demo agent used for local register_with_crew() testing."""

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "done",
            "message": "Demo task executed successfully.",
            "echo": task,
        }


async def _demo_register_with_crew() -> None:
    """
    Demo: create a demo agent and register it with the Crew Orchestrator.

    Run this file directly to test the async register_with_crew() end-to-end.
    Requires the Crew Orchestrator to be available on http://localhost:8081.
    """
    agent = _DemoAgent(
        name="demo-agent",
        archetype=AgentArchetype.WORKER,
        port=8091,
    )
    result = await agent.register_with_crew()
    print("Crew registration result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(_demo_register_with_crew())