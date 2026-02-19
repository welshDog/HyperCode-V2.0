# HyperCode V2.0 - The Cognitive Architecture

> "You do not just write code; you craft cognitive architectures."

## Why HyperCode Exists 🤯

**I built this because I don’t want anyone to suffer like I did.**

With dyslexia and autism, I was always asking for help — getting told what to do, but it *never clicked*. Instructions froze me. They didn’t sink in on the first try. Or the second. It took four or five rounds.

Not because I’m slow — my brain just works differently. Traditional guides scatter.

**That’s why I created HyperCode.**
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

Get the entire ecosystem running in **under 2 minutes**.

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/welshDog/HyperCode-V2.0.git
   cd HyperCode-V2.0
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys (Anthropic/OpenAI)
   ```

3. **Launch the Stack**
   ```bash
   docker compose up -d
   ```

4. **Access the Interfaces**
   - 🖥️ **Web Interface**: `http://localhost:3000`
   - 📊 **Grafana**: `http://localhost:3001` (User: `admin` / Pass: `admin`)
   - 📈 **Prometheus**: `http://localhost:9090`
   - 📝 **API Docs**: `http://localhost:8000/docs`

> **See [DEPLOYMENT_SUMMARY_ONE_PAGE.md](DEPLOYMENT_SUMMARY_ONE_PAGE.md) for a quick operational reference.**

---

## 🏗️ Architecture

See [docs/architecture.md](docs/architecture.md) for detailed system design.

## 🧠 Hyper AI File System (HAFS)

HyperCode V2.0 features a revolutionary **Cognitive File System** that turns the codebase into a living, intelligent entity.

-   **Semantic Search**: Find code by meaning, not just filename.
-   **Predictive Context**: The system guesses what files you need next.
-   **Self-Healing**: Agents can diagnose and fix their own errors using HAFS.
-   **Neural Visualization**: See your codebase as a connected graph.

👉 **[Read the HAFS User Guide](docs/guides/HAFS_USER_GUIDE.md)** to get started.

## 📂 Project Structure

- **src/**: Source code for all services.
  - `hypercode-core`: FastAPI backend service.
  - `hyperflow-editor`: React/Vite frontend editor.
  - `hypercode-engine`: Core execution engine.
  - `broski-terminal`: Frontend terminal interface.
  - `agents`: Autonomous agent system and specialized agents.
- **config/**: Configuration files.
  - `docker`: Docker configuration and build scripts.
  - `monitoring`: Prometheus and Grafana configs.
  - `nginx`: Nginx configuration.
- **docs/**: Comprehensive documentation.
- **scripts/**: Utility scripts for deployment and maintenance.
- **tests/**: Test suites.

## 🛡️ Development Workflow & Backup

We enforce strict development practices to ensure stability:
- **CI/CD Pipelines**: Automated testing, linting, and security scans on every push.
- **Branch Protection**: Direct pushes to `main` are blocked. PRs require approval and passing checks.
- **Backup Strategy**: Regular snapshots and GitHub mirroring. See [BACKUP_STRATEGY.md](BACKUP_STRATEGY.md) for details.

## 1️⃣ README snippet – “Status + Proof”

You can paste this under something like `## Status` or `## Operational Proof`.

```md
## 🧪 Status & Operational Proof

HyperCode V2.0 is not just a concept – it’s running as a real multi-agent swarm.

- 15/15 containers healthy: `hypercode-core`, `hafs-service`, `crew-orchestrator`, and all specialist agents. [file:16]
- Core endpoints live:
  - `GET /health` → `{"status":"healthy"}` [file:16]
  - `GET /ready` → `{"database":"connected","redis":"connected"}` [file:16]
- Key specialist agents (backend, QA, project strategy, database) have been running **stably for 40–60+ minutes** with:
  - No `ModuleNotFoundError`
  - No 401 auth errors
  - Passing healthchecks (HTTP 200) [file:16]

Recent recovery work included:
- Fixing a crash in `/agents/bible` via robust, Docker-safe path resolution. [file:16]
- Wiring agent authentication with `HYPERCODE_API_KEY` / `API_KEY` and consistent headers. [file:16]
- Increasing DB connection capacity and mounting shared `event_bus.py` into all agents. [file:16]
- Extending `hypercode-core` healthcheck `start_period` to allow clean startup. [file:16]

👉 See `FIXES_FOR_UNHEALTHY_AGENTS.md` for the full incident + recovery timeline. [file:16]
```

***

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](.github/CONTRIBUTING.md) for our code of conduct, commit message conventions, and pull request process.
