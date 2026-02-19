# 🤖 HyperCode Agent Crew - Docker Setup

Complete Docker configuration for running your 8-agent AI development team.

## 📋 Quick Start

### 1. Prerequisites
- Docker & Docker Compose installed
- Anthropic API key
- 4GB+ RAM available

### 2. Setup
```bash
# Copy environment file
cp .env.agents.example .env.agents

# Edit and add your Anthropic API key
nano .env.agents

# Build and start all agents
docker-compose -f docker-compose.agents.yml --env-file .env.agents up -d
```

### 3. Verify Setup
```bash
# Check all services are running
docker-compose -f docker-compose.agents.yml ps

# Test orchestrator health
curl http://localhost:8080/health

# Check agent status
curl http://localhost:8080/agents/status
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│     Crew Orchestrator (Port 8080)      │
│         FastAPI Coordination            │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴──────────┐
       │                  │
┌──────▼──────┐    ┌─────▼──────┐
│  Strategist │    │  Architect │
│  (Tier 1)   │    │  (Tier 1)  │
│ Port 8001   │    │ Port 8008  │
└──────┬──────┘    └─────┬──────┘
       │                  │
       └────────┬─────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐  ┌───▼───┐  ┌───▼────┐
│Frontend│  │Backend│  │Database│
│  8002  │  │  8003 │  │  8004  │
└────────┘  └───────┘  └────────┘
    │           │           │
    └───────────┼───────────┘
                │
    ┌───────────┼──────────┐
    │           │          │
┌───▼──┐  ┌────▼───┐  ┌──▼─────┐
│  QA  │  │ DevOps │  │Security│
│ 8005 │  │  8006  │  │  8007  │
└──────┘  └────────┘  └────────┘
```

## 🎯 Usage Examples

### Plan a Feature
```bash
curl -X POST http://localhost:8080/plan \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a shopping cart feature with checkout",
    "context": {
      "tech_stack": "Next.js, FastAPI, PostgreSQL"
    }
  }'
```

### Execute with Specific Agent
```bash
curl -X POST http://localhost:8080/agent/frontend-specialist/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "frontend-specialist",
    "message": "Create a responsive product card component",
    "context": {}
  }'
```

### Start a Workflow
```bash
# Feature development workflow
curl -X POST http://localhost:8080/workflow/feature \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "feature",
    "description": "User authentication system",
    "requirements": {
      "auth_method": "JWT",
      "providers": ["email", "google"]
    }
  }'
```

### Check Task Status
```bash
curl http://localhost:8080/task/task_20240205_143022
```

## 🔧 Agent Services

| Agent | Port | Model | Purpose |
|-------|------|-------|---------|
| **Orchestrator** | 8080 | - | Coordination & API |
| **Project Strategist** | 8001 | Opus | Planning & delegation |
| **Frontend Specialist** | 8002 | Sonnet | UI/UX development |
| **Backend Specialist** | 8003 | Sonnet | API & business logic |
| **Database Architect** | 8004 | Sonnet | Schema & queries |
| **QA Engineer** | 8005 | Sonnet | Testing & validation |
| **DevOps Engineer** | 8006 | Sonnet | CI/CD & infrastructure |
| **Security Engineer** | 8007 | Sonnet | Security audits |
| **System Architect** | 8008 | Opus | Architecture design |

## 📁 Project Structure

```
agents/
├── base-agent/              # Shared base agent class
│   ├── Dockerfile
│   ├── agent.py
│   └── requirements.txt
├── crew-orchestrator/       # Central coordination service
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── 01-frontend-specialist/
├── 02-backend-specialist/
├── 03-database-architect/
├── 04-qa-engineer/
├── 05-devops-engineer/
├── 06-security-engineer/
├── 07-system-architect/
└── 08-project-strategist/

Configuration_Kit/           # Hive Mind (mounted as volume)
├── Team_Memory_Standards.md
└── Agent_Skills_Library.md
```

## 🧠 Hive Mind Integration

All agents share knowledge through:
- **Team_Memory_Standards.md** - Coding standards, conventions
- **Agent_Skills_Library.md** - Reusable skills & patterns
- **Redis** - Real-time task coordination
- **PostgreSQL** - Persistent memory & history

## 🐳 Docker Commands

```bash
# Start all agents
docker-compose -f docker-compose.agents.yml up -d

# View logs
docker-compose -f docker-compose.agents.yml logs -f

# Stop all agents
docker-compose -f docker-compose.agents.yml down

# Rebuild specific agent
docker-compose -f docker-compose.agents.yml build frontend-specialist
docker-compose -f docker-compose.agents.yml up -d frontend-specialist

# Scale specialists (if needed)
docker-compose -f docker-compose.agents.yml up -d --scale backend-specialist=2

# View resource usage
docker stats
```

## 🔍 Monitoring

Access the agent dashboard at: http://localhost:8090

View individual agent health:
- Orchestrator: http://localhost:8080/health
- Project Strategist: http://localhost:8001/health
- Frontend: http://localhost:8002/health
- Backend: http://localhost:8003/health

## 🔐 Security Best Practices

1. **Never commit `.env.agents`** - Contains API keys
2. **Use secrets management** for production (Docker Secrets, Vault)
3. **Restrict network access** - Only expose orchestrator publicly
4. **Regular updates** - Keep base images updated
5. **Resource limits** - Already configured in compose file

## 🚀 Scaling for Production

### Kubernetes Deployment
```bash
# Convert Docker Compose to Kubernetes
kompose convert -f docker-compose.agents.yml

# Apply to cluster
kubectl apply -f .
```

### Load Balancing
Add multiple instances of specialist agents:
```yaml
deploy:
  replicas: 3
```

### Horizontal Pod Autoscaling (K8s)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-specialist-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-specialist
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 🐛 Troubleshooting

### Agent not starting
```bash
# Check logs
docker logs project-strategist

# Verify API key is set
docker exec project-strategist env | grep ANTHROPIC
```

### Redis connection issues
```bash
# Test Redis
docker exec agent-redis redis-cli ping

# Restart Redis
docker-compose -f docker-compose.agents.yml restart redis
```

### Out of memory
```bash
# Check current usage
docker stats

# Increase Docker Desktop memory allocation
# Settings > Resources > Memory > 8GB+
```

## 📚 Integration with Trae

Mount your Trae workspace:
```yaml
volumes:
  - ${TRAE_WORKSPACE_PATH}:/workspace:ro
```

Configure MCP tools in agent environment:
```yaml
environment:
  - MCP_GITHUB_TOKEN=${GITHUB_TOKEN}
  - MCP_FILESYSTEM_ROOT=/workspace
```

## 🎓 Next Steps

1. ✅ Deploy to production with Kubernetes
2. ✅ Add monitoring with Prometheus + Grafana
3. ✅ Implement webhook integrations (GitHub, Slack)
4. ✅ Create custom agents for your domain
5. ✅ Set up CI/CD pipeline for agent updates

---

**Built with ❤️ for HyperCode V2.0**
