# HyperCode Agent Crew - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Applications                          │
│  (Web UI, CLI, API Clients, Trae Integration)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Crew Orchestrator (FastAPI)                        │
│  - Task routing & delegation                                     │
│  - Agent coordination                                            │
│  - Workflow management                                           │
│  - Redis pub/sub for real-time updates                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
        ┌───────────────────┐   ┌────────────────┐
        │  Redis (Message   │   │  PostgreSQL    │
        │  Queue & Cache)   │   │  (Task History)│
        └───────────────────┘   └────────────────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
         ▼          ▼          ▼
┌────────────┐ ┌──────────┐ ┌──────────────┐
│ Strategist │ │Architect │ │  Specialists │
│  (Tier 1)  │ │ (Tier 1) │ │   (Tier 2)   │
└──────┬─────┘ └────┬─────┘ └──────┬───────┘
       │            │               │
       └────────────┼───────────────┘
                    │
        ┌───────────┼───────────────┐
        │           │               │
        ▼           ▼               ▼
 ┌──────────┐ ┌──────────┐  ┌────────────┐
 │ Frontend │ │ Backend  │  │  Database  │
 │    QA    │ │  DevOps  │  │  Security  │
 └──────────┘ └──────────┘  └────────────┘
        │           │               │
        └───────────┼───────────────┘
                    │
                    ▼
         ┌────────────────────┐
         │    Hive Mind       │
         │  (Shared Memory)   │
         │  - Team Standards  │
         │  - Skills Library  │
         └────────────────────┘
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
3. Returns to user
4. Archives in PostgreSQL for history

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
- **pgvector**: Vector embeddings (future)

### AI
- **Anthropic Claude**: LLM (Opus, Sonnet)
- **CrewAI**: Agent framework (optional)

## Scalability

### Horizontal Scaling
```yaml
# Scale specialist agents
docker-compose up --scale backend-specialist=3
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
- Stored in environment variables
- Never committed to git
- Rotated regularly

### Network Isolation
- Agents on private network
- Only orchestrator exposed
- TLS for external communication

### Container Security
- Non-root users
- Minimal base images
- Regular security scans

## Monitoring

### Health Checks
- HTTP endpoints on all services
- 30-second intervals
- Auto-restart on failure

### Metrics (Future)
- Prometheus for metrics
- Grafana for visualization
- Alert on SLA violations

### Logging
- Structured JSON logs
- Centralized via ELK/Loki
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

### Implementation
- Mounted as read-only volumes
- Loaded into agent context
- Updated via configuration files

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

### CI/CD Integration
- Trigger on deployment
- Run agent-based tests
- Quality gates

## Future Enhancements

1. **Vector Memory**: Store past solutions in pgvector
2. **Learning Loop**: Fine-tune on project-specific patterns
3. **Multi-project**: Separate workspaces per project
4. **Human-in-the-Loop**: Approval workflow for changes
5. **Telemetry**: Track agent performance metrics
