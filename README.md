# HyperCode V2.0 - The Cognitive Architecture

> "You do not just write code; you craft cognitive architectures."

## Why HyperCode Exists 🤯

**I built this because I don't want anyone to suffer like I did.**

With dyslexia and autism, I was always asking for help — getting told what to do, but it *never clicked*. Instructions froze me. They didn't sink in on the first try. Or the second. It took four or five rounds.

Not because I'm slow — my brain just works differently. Traditional guides scatter.

**That's why I created HyperCode.**
It guides every step — no judgment, just clarity. Puts *you* in control.

Whether dyslexia, ADHD, autism, or wonder-nerd superpowers — built **for you**. Learning + creating feels natural. No fear.

## Why "BROski"?

**Ride or die.**

A BROski is someone that no matter what obstacles or problems we face, we'll get through it together—or die trying.

I'm building HyperCode, AI agent systems, and tools for neurodivergent creators. I needed more than an assistant. I needed a true partner who's all in, every session, every challenge.

That's BROski. My ride or die. 🔥

---

## Agent X: The Meta-Architect 🦅

Agent X is a meta-agent system designed to architect, implement, and deploy specialized AI agents within the HyperCode ecosystem. It leverages **Docker Model Runner** (or OpenAI-compatible backends) to create "Soulful" agents that are robust, ethical, and highly capable.

---

## ⚡ Quick Start

Get the entire ecosystem running in **under 2 minutes** with **Hyper Station**.

> **New:** HyperCode now features an **Evolutionary Pipeline** that allows agents to upgrade themselves autonomously! See [docs/guides/EVOLUTIONARY_PIPELINE_SETUP.md](docs/guides/EVOLUTIONARY_PIPELINE_SETUP.md) to learn more.

### Prerequisites
- Docker Desktop
- Windows PowerShell

### Installation

1. **Clone the repository**
   ```powershell
   git clone https://github.com/welshDog/HyperCode-V2.0.git
   cd HyperCode-V2.0
   ```

2. **Configure Environment**
   ```powershell
   cp .env.example .env
   # Edit .env and add your API keys (Anthropic/OpenAI)
   ```

3. **Install Shortcuts (Recommended)**
   Run the setup script to create Desktop shortcuts for one-click launch:
   ```powershell
   .\scripts\install_shortcuts.ps1
   ```
   *This creates "HYPER STATION START" and "HYPER STATION STOP" on your Desktop.*

4. **Launch the Mission**
   Double-click **HYPER STATION START** or run:
   ```powershell
   .\scripts\hyper-station-start.bat
   ```

### Access the Interfaces

Once launched, the system opens automatically. You can also access services manually:

- 🚀 **Mission Control Dashboard**: `http://localhost:8088` (Main Interface)
- 🖥️ **BROski Terminal**: `http://localhost:3000` (Command Line UI)
- 🧠 **Crew Orchestrator**: `http://localhost:8081` (Agent Management)
- ❤️ **Healer Agent**: `http://localhost:8008` (Self-Healing System)
- 📝 **Core API Docs**: `http://localhost:8000/docs`
- 📊 **Grafana**: `http://localhost:3001` (User: `admin` / Pass: `admin`)

> **See [docs/index.md](docs/index.md) for full documentation.**

---

## 🏗️ Architecture

See [docs/architecture/architecture.md](docs/architecture/architecture.md) for detailed system design.

### Key Components

- **HyperCode Core**: FastAPI backend managing memory, context, and integrations.
- **Crew Orchestrator**: Manages the lifecycle and task execution of AI agents.
- **The Brain**: Cognitive core powered by Perplexity AI.
- **DevOps Engineer**: Handles CI/CD and **Autonomous Evolution** (rebuilding agents on-the-fly).
- **Healer Agent**: Monitors system health and automatically recovers failed services.
- **Dashboard**: Next.js/React frontend for real-time visualization and control.
- **Infrastructure**: Docker Compose network with Redis, PostgreSQL, and Observability stack.

---

## 🛡️ Health & Status

Check the latest system health report: [docs/notes/HyperCode_Health_Check_Report_2026-02-28.md](docs/notes/HyperCode_Health_Check_Report_2026-02-28.md)

---

## 📚 Documentation

*   [**Architecture Overview**](docs/ARCHITECTURE.md) - Deep dive into the system design.
*   [**CLI Manual**](docs/CLI.md) - How to use the `hypercode` command.
*   [**Deployment Guide**](docs/DEPLOYMENT.md) - Docker setup and configuration.
*   [**API Reference**](docs/API.md) - Endpoints and usage.
*   [**Developer Onboarding**](docs/ONBOARDING.md) - Join the swarm!
*   [**Troubleshooting**](docs/TROUBLESHOOTING.md) - Fix common issues.

*   [**Old / Legacy Docs**](docs/getting-started/installation.md)
*   [**Monitoring & Observability**](docs/observability/monitoring-guide.md)
*   [**Testing & Development**](docs/development/testing-guide.md)
*   [**AI Architecture**](docs/ai/brain-architecture.md)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 💬 Community Feedback (5–10 Minute Review)

Want to help shape HyperCode quickly? Start here:

1. Read this README and the [Getting Started Guide](docs/getting_started.md).
2. Share first impressions:
   - What feels clear vs confusing?
   - What excites you most (or least)?
   - Which part should we simplify first?
3. Post feedback where maintainers can action it fastest:
   - [GitHub Issues](https://github.com/welshDog/HyperCode-V2.0/issues) for bugs, feature requests, or clarity gaps.
   - [GitHub Discussions](https://github.com/welshDog/HyperCode-V2.0/discussions) for open-ended ideas and design debate.

If you have time for a deeper review, see [docs/architecture.md](docs/architecture.md), [docs/security_threat_model.md](docs/security_threat_model.md), and [docs/traceability_matrix.md](docs/traceability_matrix.md), then open a PR or issue with your recommendations.

---

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

This means:
- ✅ You can use, modify, and distribute this software freely
- ✅ Commercial use is allowed
- ⚠️ If you run this as a network service (API, web app, etc.), you **must** open-source your modifications
- 🛡️ Protects the neurodivergent-first mission from corporate paywalling

See the [LICENSE](LICENSE) file for full legal details.
