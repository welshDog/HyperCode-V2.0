# 🚀 HyperCode V2.0 Quickstart

**Goal:** Run the entire ecosystem (Agents, API, Dashboard, Observability) in under 2 minutes.

## 📋 Prerequisites

- **Docker & Docker Compose** (Desktop 4.0+)
- **Git**
- **Node.js 18+** (Optional, only for local frontend development)

## ⚡ Steps

### 1. Clone the Repository
```bash
git clone https://github.com/welshDog/HyperCode-V2.0.git
cd HyperCode-V2.0
```

### 2. Configure Environment
Set up your environment variables (API keys, Database credentials).
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY / OPENAI_API_KEY
```

### 3. Launch the Stack
Start all services including the Agent Swarm, Core API, and Observability stack.
```bash
docker compose up -d
```

### 4. Verify Services
Check that all 23+ containers are healthy.
```bash
docker compose ps
```

## 🖥️ Access Interfaces

| Service | URL | Credentials (Default) |
|---------|-----|-----------------------|
| **Web Terminal** | [http://localhost:3000](http://localhost:3000) | N/A |
| **Grafana** | [http://localhost:3001](http://localhost:3001) | `admin` / `admin` |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | N/A |
| **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | N/A |
| **Jaeger** | [http://localhost:16686](http://localhost:16686) | N/A |

## 🎮 Run Your First Mission

1. Open the **Web Terminal** at `http://localhost:3000`.
2. Navigate to the **Agents** tab.
3. Select **Coder Agent**.
4. Type: `"Create a Python script that calculates the Fibonacci sequence."`
5. Watch the agent think, plan, and code in real-time.

## 🛑 Stop Services
```bash
docker compose down
```

---
> *Need help? Check [DEPLOYMENT_SUMMARY_ONE_PAGE.md](../DEPLOYMENT_SUMMARY_ONE_PAGE.md) for quick troubleshooting.*
