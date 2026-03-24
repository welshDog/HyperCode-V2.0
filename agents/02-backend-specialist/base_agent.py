"""
HyperCode Base Agent - Fixed
Uses anthropic client instead of broken PERPLEXITY import
"""
import asyncio
import os
from dataclasses import dataclass, field
from typing import Optional

try:
    import anthropic
    AsyncAnthropic = anthropic.AsyncAnthropic
except ImportError:
    AsyncAnthropic = None

try:
    from structlog import get_logger
except ImportError:
    import logging
    def get_logger(): return logging.getLogger(__name__)


@dataclass
class AgentConfig:
    name: str = "backend-specialist"
    model: str = os.getenv("AGENT_MODEL", "claude-3-5-haiku-20241022")
    api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    max_tokens: int = 2000


class ProjectMemory:
    def __init__(self):
        self._apis = []
    def get_project_context(self): return {"available_apis": self._apis}
    def add_api_endpoint(self, endpoint: str): self._apis.append(endpoint)


class AgentMemory:
    def query_relevant_context(self, task: str) -> str: return ""


class ApprovalSystem:
    async def request_approval(self, agent, action, payload, timeout=300):
        return {"status": "approved"}


class BaseAgent:
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.logger = get_logger()
        self.client = AsyncAnthropic(api_key=self.config.api_key) if AsyncAnthropic and self.config.api_key else None
        self.agent_memory = AgentMemory()
        self.project_memory = ProjectMemory()
        self.approval_system = ApprovalSystem()

    async def process_task(self, task: str, context: dict, requires_approval: bool = False):
        raise NotImplementedError("Subclasses must implement process_task")

    def run(self):
        asyncio.run(self.process_task("startup check", {}, False))
