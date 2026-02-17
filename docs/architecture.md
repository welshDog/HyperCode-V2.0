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

    subgraph "Background Processing"
        Celery[Celery Worker]
    end

    Strat -->|Task| Redis
    Arch -->|Standards| Redis
    Redis -->|Pub/Sub| Specialist Swarm
    Specialist Swarm -->|Results| Redis
    Redis -->|Aggregation| API
    
    API -->|Metrics| Prom
    Prom --> Graf
    
    Celery -->|Tasks| Redis
    Redis -->|Results| Celery
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

## Communication Flow

### 1. Task Submission
```
User → Orchestrator → Project Strategist → Breakdown → Specialists
```

### 2. Inter-Agent Communication
```
Agent A → Redis Pub/Sub → Agent B
         ↓
    PostgreSQL (persistence)
```

### 3. Result Aggregation
```
Specialists → Results → Orchestrator → Client
                ↓
           Task History (PostgreSQL)
```

## Data Flow

### Task Planning
1. User submits task to Orchestrator
2. Orchestrator forwards to Project Strategist
3. Strategist analyzes and creates subtasks
4. Subtasks stored in Redis with status
5. Specialists notified via Redis pub/sub

### Task Execution
1. Specialist receives task from queue
2. Loads Hive Mind context (standards, skills)
3. Calls Claude API with enriched prompt
4. Stores result in Redis
5. Notifies Orchestrator of completion

### Result Collection
1. Orchestrator monitors Redis for completions
2. Aggregates specialist results

## Background Processing

### Celery Worker
- **Role**: Asynchronous task execution for long-running operations.
- **Responsibilities**:
  - Complex code analysis
  - Large-scale refactoring
  - Batch data processing
  - Mission execution management
- **Dependencies**:
  - Redis (Broker & Backend)
  - **OpenAI API Key**: Required for LLM-based operations (Critical dependency).
  - PostgreSQL (Data persistence)

### Auto-Restart Policy
- All services are configured with `restart: always` or `unless-stopped` to ensure high availability.
- `health_check.py` verifies the status of all containers and critical endpoints.

## Observability Stack
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
