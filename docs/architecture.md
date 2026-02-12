# HyperCode Agent Crew - Architecture

## System Overview

```mermaid
graph TD
    User[Client Applications] -->|HTTP/WS| API[Crew Orchestrator]
    API -->|Delegation| Strat[Project Strategist]
    API -->|Coordination| Arch[System Architect]
    
    subgraph "Data Layer"
        Redis[(Redis Cache & Queue)]
        DB[(PostgreSQL History)]
    end
    
    subgraph "Specialist Swarm (Tier 2)"
        FE[Frontend Specialist]
        BE[Backend Specialist]
        QA[QA Engineer]
        DevOps[DevOps Engineer]
        Sec[Security Engineer]
    end
    
    subgraph "Observability"
        Prom[Prometheus]
        Graf[Grafana]
        Jaeger[Jaeger Tracing]
    end

    Strat -->|Task| Redis
    Arch -->|Standards| Redis
    Redis -->|Pub/Sub| Specialist Swarm
    Specialist Swarm -->|Results| Redis
    Redis -->|Aggregation| API
    
    API -->|Metrics| Prom
    Prom --> Graf
```

## Agent Hierarchy

### Tier 1: Strategic Agents (Orchestrators)
- **Project Strategist**: Plans, breaks down tasks, delegates
- **System Architect**: Defines architecture, patterns, standards

**Model**: Claude Opus (highest reasoning capability)
**Responsibilities**: High-level planning, decision-making

### Tier 2: Specialist Agents (Executors)
- **Frontend Specialist**: UI/UX, React, Next.js
- **Backend Specialist**: APIs, business logic, Python
- **Database Architect**: Schema, queries, optimization
- **QA Engineer**: Testing, validation, quality assurance
- **DevOps Engineer**: CI/CD, Docker, Kubernetes
- **Security Engineer**: Security audits, vulnerability scanning

**Model**: Claude Sonnet (fast, efficient)
**Responsibilities**: Specialized task execution

## Technology Stack

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Local orchestration
- **Kubernetes**: Production orchestration (optional)

### Backend
- **FastAPI**: REST API framework
- **Python 3.11**: Programming language
- **Uvicorn**: ASGI server

### Message Queue & Cache
- **Redis**: Task queue, pub/sub, caching
- **Redis Streams**: Event log

### Database
- **PostgreSQL**: Task history, agent memory
- **pgvector**: Vector embeddings

### AI
- **Anthropic Claude**: LLM (Opus, Sonnet)
- **Ollama**: Local LLM inference (optional fallback)
- **CrewAI**: Agent framework

## Scalability

### Horizontal Scaling
```bash
# Scale specialist agents
docker compose up -d --scale backend-specialist=3
```

### Load Balancing
- nginx/Traefik for orchestrator
- Redis queue distributes tasks
- Multiple specialist instances

### Resource Allocation
- Tier 1 agents: 0.75 CPU, 768MB RAM
- Tier 2 agents: 0.5 CPU, 512MB RAM
- Orchestrator: 1 CPU, 1GB RAM

## Security

### API Keys
- Stored in `.env` file (via `.env.example`)
- Never committed to git
- Rotated regularly

### Network Isolation
- Agents on private network (`backend-net`)
- Only orchestrator exposed
- TLS for external communication

## Monitoring (Active)

### Health Checks
- HTTP endpoints on all services
- 30-second intervals
- Auto-restart on failure

### Observability Stack
- **Prometheus**: Metrics collection
- **Grafana**: Visual dashboards (http://localhost:3001)
- **Jaeger**: Distributed tracing

### Logging
- Structured JSON logs
- Centralized via ELK/Loki (optional)
- Correlation IDs for tracing

## Hive Mind (Shared Knowledge)

### Team Memory Standards
- Coding conventions
- Best practices
- Project-specific rules
- Updated by all agents

### Skills Library
- Reusable functions
- Common patterns
- Tested solutions
- Version controlled

## Integration Points

### Trae Integration
```yaml
volumes:
  - ${TRAE_WORKSPACE}:/workspace:ro
environment:
  - TRAE_MCP_ENABLED=true
```

### GitHub Integration
- Webhooks for issues → tasks
- PR review by agents
- Commit on completion

## Future Enhancements
1. **Learning Loop**: Fine-tune on project-specific patterns
2. **Multi-project**: Separate workspaces per project
3. **Human-in-the-Loop**: Approval workflow for changes
