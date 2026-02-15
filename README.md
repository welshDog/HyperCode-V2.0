# Agent X: The Meta-Architect 🦅

> "You do not just write code; you craft cognitive architectures."

Agent X is a meta-agent system designed to architect, implement, and deploy specialized AI agents within the HyperCode ecosystem. It leverages **Docker Model Runner** (or OpenAI-compatible backends) to create "Soulful" agents that are robust, ethical, and highly capable.

---

## 🚀 Quick Start

> **Infrastructure & Health**: For how the platform runs in production, see [docs/infra/status-and-health.md](docs/infra/status-and-health.md).

Get your first agent running in 3 commands:

```powershell
# 1. Enable Docker Model Runner (Prerequisite)
# Docker Desktop -> Settings -> AI -> Enable Model Runner

# 2. Start the Brain (Qwen 2.5 Coder 7B recommended)
docker model run -d hf.co/Qwen/Qwen2.5-Coder-7B-Instruct

# 3. Awaken HyperTutor (The first Agent X creation)
docker run -it \
  -e MODEL_NAME="hf.co/Qwen/Qwen2.5-Coder-7B-Instruct" \
  --add-host=host.docker.internal:host-gateway \
  hypercode-tutor
```

---

## 🧠 System Architecture

Agent X agents follow a tripartite biological architecture:

1.  **The Brain (Model)**
    *   **Technology**: Docker Model Runner (Local LLM) or OpenAI API.
    *   **Function**: Raw cognitive processing and reasoning.
    *   **Standard**: OpenAI-compatible API (`/v1/chat/completions`).

2.  **The Soul (System Prompt)**
    *   **File**: `SOUL.md`
    *   **Function**: Defines personality, constraints, ethics, and domain knowledge.
    *   **Philosophy**: Neurodivergent-friendly, chunked information, visual-first.

3.  **The Body (Container)**
    *   **Technology**: Docker (`python:3.11-slim`)
    *   **Function**: Execution environment, tools, and I/O.
    *   **Security**: Non-root user execution.

---

## 📚 Agent Library

| Agent Name | Role | Status | Source |
| :--- | :--- | :---: | :--- |
| **HyperTutor** | Neurodivergent-friendly HyperCode mentor | 🟢 Ready | `agents/hypercode-tutor` |
| **Orchestrator** | Multi-agent crew manager | 🟡 Planned | *Coming Soon* |
| **Architect** | System design and blueprinting | 🟡 Planned | *Coming Soon* |

---

## 🛠️ Development Guide

### Creating a New Agent

1.  **Define the Soul**: Create a `SOUL.md` using the Agent X template.
2.  **Build the Body**: Use the standard `Dockerfile` pattern.
3.  **Connect the Brain**: Ensure `agent.py` points to your model backend.

### Standard `Dockerfile` Pattern

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY SOUL.md agent.py .
RUN pip install requests && useradd -m agent
USER agent
CMD ["python", "agent.py"]
```

---

## 🗺️ Roadmap (30-60-90)

### Phase 1: Foundation (Feb 14 - Mar 14)
- [x] Agent X Meta-Architecture
- [x] HyperTutor Implementation
- [x] Docker Model Runner Integration
- [x] RBAC & Security Hardening (v2.0)
- [x] Coder Agent Standardization (FastAPI)
- [ ] Agent Factory Service (Automated creation)
- [ ] Multi-Agent Bus (Inter-agent communication)

### Phase 2: Expansion (Mar 14 - Apr 14)
- [ ] Full Crew Deployment (8 Specialized Agents)
- [ ] Visual Agent Dashboard
- [ ] Public Beta Release

### Phase 3: Ecosystem (Apr 14 - May 14)
- [ ] HyperCode V2.0 Integration
- [ ] Community Agent Marketplace
- [ ] Enterprise Governance Module

---

## 📄 Documentation

*   [Sprint Review (Feb 13, 2026)](docs/sprints/SPRINT_REVIEW_2026-02-13.md) - Historical record of the initial architecture sprint.
*   [Status Reports](PROJECT_STATUS_REPORT_TEMPLATE.md) - Project management framework.

---

*Powered by HyperCode V2.0* 🚀
