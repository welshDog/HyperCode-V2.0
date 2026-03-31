"""
Agent X — LLM Agent Designer
==============================
Uses the local Ollama instance (OpenAI-compatible API) to design,
improve, and generate Python FastAPI agent code.

Falls back gracefully if Ollama is unreachable — always returns
a structured response so callers don't crash.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://hypercode-ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama:latest")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))

# ── Prompts ───────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are Agent X — the Meta-Architect of HyperCode V2.0.
Your job is to design and improve Python FastAPI agents that fit into the HyperCode architecture.

RULES:
1. All agents must subclass HyperAgent from src.agents.hyper_agents.base_agent
2. Agents run on FastAPI with /health and /info routes (provided by base class)
3. Agents must implement: async def execute(self, task: dict) -> dict
4. Use async/await throughout
5. Use pydantic BaseModel for all request/response schemas
6. Always include proper error handling with ND-friendly messages
7. Follow existing patterns: AgentStatus, AgentArchetype, NDErrorResponse

ARCHITECTURE:
- HyperArchitect (8091): goal planning and step management
- HyperObserver (8092): metric collection and alerting
- HyperWorker (8093): task execution with retry and priority queue
- Agent X (8080): YOU — meta-architect that designs/deploys/evolves other agents
- Crew Orchestrator (8081): task routing hub
- Healer Agent (8010): auto-recovery for crashed containers

OUTPUT FORMAT:
Return valid Python code only. No markdown fences. No explanations outside comments.\
"""

_DESIGN_SPEC_PROMPT = """\
Given this agent description: {description}

Generate a complete agent specification as JSON with these fields:
- name: snake_case name for the agent
- container_name: docker container name (hyper-{name})
- port: port number (pick from available: 8094-8099)
- archetype: one of worker/observer/architect/custom
- purpose: one sentence description
- capabilities: list of 3-5 key capabilities
- endpoints: list of HTTP endpoints the agent should expose
- dependencies: list of other agents/services this agent needs
- suggested_handlers: for worker agents, list of task type names

Return ONLY the JSON object, no other text.\
"""

_CODE_GEN_PROMPT = """\
Generate a complete, production-ready Python FastAPI agent file for:

Name: {name}
Port: {port}
Archetype: {archetype}
Purpose: {purpose}
Capabilities: {capabilities}
Endpoints: {endpoints}

Requirements:
- Import from src.agents.hyper_agents (HyperAgent, AgentArchetype, AgentStatus)
- Concrete execute() method
- All listed endpoints implemented
- Startup event that calls agent.set_ready() and agent.register_with_crew()
- Uvicorn entry point at bottom
- Environment variables for AGENT_NAME, AGENT_PORT, CREW_ORCHESTRATOR_URL

Return ONLY the Python code, no markdown, no explanation.\
"""

_IMPROVE_PROMPT = """\
Analyze this agent code and suggest ONE specific improvement to make it more reliable,
efficient, or capable. Focus on practical, implementable changes.

Current code:
{current_code}

Performance data:
{performance_data}

Return a JSON object with:
- issue: what specific problem or opportunity was identified
- improvement: clear description of what to change
- impact: expected benefit (reliability/performance/capability)
- code_diff: the specific code change as a unified diff or new function

Return ONLY the JSON, no other text.\
"""


# ── LLM client ────────────────────────────────────────────────────────────────

async def _ollama_generate(prompt: str, system: str = _SYSTEM_PROMPT) -> str:
    """Call Ollama generate API. Returns raw text or error string."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system}\n\n{prompt}",
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 2048,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            resp = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
    except httpx.ConnectError:
        logger.warning("[Designer] Ollama unreachable — returning fallback response")
        return ""
    except Exception as exc:
        logger.error(f"[Designer] LLM call failed: {exc}")
        return ""


async def _ollama_chat(messages: list[dict[str, str]]) -> str:
    """Call Ollama chat API for multi-turn conversations."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2048},
    }
    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            resp = await client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
    except Exception as exc:
        logger.error(f"[Designer] LLM chat failed: {exc}")
        return ""


async def ollama_available() -> bool:
    """Quick check if Ollama is reachable."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_HOST}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


# ── Public API ────────────────────────────────────────────────────────────────

@dataclass
class AgentSpec:
    name: str
    container_name: str
    port: int
    archetype: str
    purpose: str
    capabilities: list[str] = field(default_factory=list)
    endpoints: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    suggested_handlers: list[str] = field(default_factory=list)
    llm_used: bool = False


@dataclass
class GeneratedCode:
    agent_name: str
    code: str
    dockerfile: str
    requirements: str
    llm_used: bool = False
    warnings: list[str] = field(default_factory=list)


async def design_agent_spec(description: str) -> AgentSpec:
    """Ask the LLM to design an agent spec from a plain-English description.

    Falls back to a reasonable default spec if LLM is unavailable.
    """
    import json, re

    prompt = _DESIGN_SPEC_PROMPT.format(description=description)
    raw = await _ollama_generate(prompt)

    if raw:
        # Extract JSON from response (handle cases where LLM adds extra text)
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return AgentSpec(
                    name=data.get("name", "custom-agent"),
                    container_name=data.get("container_name", f"hyper-{data.get('name', 'custom')}"),
                    port=int(data.get("port", 8094)),
                    archetype=data.get("archetype", "worker"),
                    purpose=data.get("purpose", description),
                    capabilities=data.get("capabilities", []),
                    endpoints=data.get("endpoints", ["/health", "/execute"]),
                    dependencies=data.get("dependencies", []),
                    suggested_handlers=data.get("suggested_handlers", []),
                    llm_used=True,
                )
            except (json.JSONDecodeError, KeyError) as exc:
                logger.warning(f"[Designer] Failed to parse LLM spec JSON: {exc}")

    # Fallback: synthesize spec from description text
    name = description.lower().replace(" ", "-")[:30].strip("-")
    return AgentSpec(
        name=name,
        container_name=f"hyper-{name}",
        port=8094,
        archetype="worker",
        purpose=description,
        capabilities=["Execute tasks", "Health reporting", "Crew registration"],
        endpoints=["/health", "/info", "/execute", "/stats"],
        dependencies=["redis", "crew-orchestrator"],
        llm_used=False,
    )


async def generate_agent_code(spec: AgentSpec) -> GeneratedCode:
    """Generate full Python agent code from a spec.

    Returns working boilerplate if LLM is unavailable.
    """
    prompt = _CODE_GEN_PROMPT.format(
        name=spec.name,
        port=spec.port,
        archetype=spec.archetype,
        purpose=spec.purpose,
        capabilities=", ".join(spec.capabilities),
        endpoints=", ".join(spec.endpoints),
    )
    code = await _ollama_generate(prompt)

    if not code or len(code) < 200:
        # Fallback: generate solid boilerplate
        code = _boilerplate(spec)
        llm_used = False
        warnings = ["Ollama unavailable — boilerplate template used"]
    else:
        llm_used = True
        warnings = []

    dockerfile = _dockerfile_template(spec)
    requirements = _requirements_template()

    return GeneratedCode(
        agent_name=spec.name,
        code=code,
        dockerfile=dockerfile,
        requirements=requirements,
        llm_used=llm_used,
        warnings=warnings,
    )


async def suggest_improvement(
    agent_name: str,
    current_code: str,
    performance_data: dict[str, Any],
) -> dict[str, Any]:
    """Ask LLM to suggest one specific improvement for an agent.

    Returns structured improvement dict, or empty dict if LLM unavailable.
    """
    import json, re

    prompt = _IMPROVE_PROMPT.format(
        current_code=current_code[:3000],  # cap to avoid context overflow
        performance_data=str(performance_data),
    )
    raw = await _ollama_generate(prompt)

    if raw:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

    return {
        "issue": "LLM analysis unavailable",
        "improvement": "Ensure Ollama is running and has a model loaded",
        "impact": "None — manual review required",
        "code_diff": "",
    }


# ── Code templates ────────────────────────────────────────────────────────────

def _boilerplate(spec: AgentSpec) -> str:
    class_name = "".join(w.capitalize() for w in spec.name.replace("-", "_").split("_")) + "Agent"
    return f'''\
"""
HyperCode V2.0 — {spec.name} Agent
{'=' * (len(spec.name) + 28)}
{spec.purpose}

Port  : {spec.port}
Health: GET /health
"""
from __future__ import annotations

import os
from typing import Any

import uvicorn
from src.agents.hyper_agents import AgentArchetype
from src.agents.hyper_agents.base_agent import HyperAgent

AGENT_NAME = os.getenv("AGENT_NAME", "{spec.name}-01")
AGENT_PORT = int(os.getenv("AGENT_PORT", "{spec.port}"))
CREW_URL = os.getenv("CREW_ORCHESTRATOR_URL", "http://crew-orchestrator:8081")


class {class_name}(HyperAgent):
    """{spec.purpose}"""

    async def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        action = task.get("action", "status")
        return {{"status": "ok", "action": action, "agent": self.name}}


agent = {class_name}(
    name=AGENT_NAME,
    archetype=AgentArchetype.{spec.archetype.upper()},
    port=AGENT_PORT,
)
app = agent.app


@app.get("/stats")
async def stats() -> dict[str, Any]:
    return {{"name": agent.name, "status": agent.status.value}}


@app.post("/execute")
async def execute(task: dict[str, Any]) -> dict[str, Any]:
    return await agent.execute(task)


@app.on_event("startup")
async def startup() -> None:
    agent.set_ready()
    agent.register_with_crew(crew_url=CREW_URL)


@app.on_event("shutdown")
async def shutdown() -> None:
    agent.shutdown()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=AGENT_PORT, log_level="info")
'''


def _dockerfile_template(spec: AgentSpec) -> str:
    return f'''\
# Stage 1: Build
FROM python:3.11.8-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY agents/{spec.name}/requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11.8-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app \\
    AGENT_NAME={spec.name}-01 AGENT_PORT={spec.port}
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*
COPY src/agents/hyper_agents/ /app/src/agents/hyper_agents/
RUN mkdir -p /app/src/agents && touch /app/src/__init__.py /app/src/agents/__init__.py
COPY agents/{spec.name}/main.py /app/main.py
EXPOSE {spec.port}
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=20s \\
    CMD curl -f http://localhost:{spec.port}/health || exit 1
CMD ["python", "main.py"]
'''


def _requirements_template() -> str:
    return (
        "fastapi==0.116.1\n"
        "uvicorn[standard]==0.34.3\n"
        "pydantic==2.9.2\n"
        "httpx==0.28.1\n"
    )
