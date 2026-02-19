# HyperCode Agent Crew - Complete Docker Setup

## 📦 What's Been Created

### ✅ Complete Docker Infrastructure

**1. Orchestration Layer**
- FastAPI-based crew orchestrator
- Task routing and delegation
- Agent coordination via Redis
- RESTful API for client interaction

**2. Base Agent Framework**
- Reusable base agent class
- Hive Mind integration (shared knowledge)
- Health checks and monitoring
- Redis-based communication

**3. All 8 Specialized Agents**
- **Project Strategist** (Tier 1) - Planning & delegation
- **System Architect** (Tier 1) - Architecture & design
- **Frontend Specialist** - React, Next.js, UI/UX
- **Backend Specialist** - FastAPI, business logic
- **Database Architect** - PostgreSQL, schema design
- **QA Engineer** - Testing, automation
- **DevOps Engineer** - CI/CD, Docker, Kubernetes
- **Security Engineer** - Security audits, OWASP

**4. Infrastructure Services**
- Redis for message queue & caching
- PostgreSQL for task history
- Agent dashboard (web UI)

**5. Development Tools**
- Makefile for easy commands
- Shell scripts (Windows & Linux)
- Docker Compose orchestration
- Environment configuration

**6. Testing & Examples**
- Test suite with pytest
- API usage examples
- Health check scripts

**7. Documentation**
- Architecture overview
- Deployment guide
- Quick start guide
- API documentation

**8. CI/CD Pipeline**
- GitHub Actions workflow
- Automated testing
- Docker image building
- Security scanning

## 🚀 Quick Start

### Option 1: Core Platform Setup (Recommended)
This option launches the Core Platform including the Terminal, Editor, and Core Services.

1. Navigate to the subdirectory:
   ```bash
   cd HyperCode-V2.0
   ```

2. Start the services:
   ```bash
   docker compose up -d --build
   ```

3. Access the interfaces:
   - **Terminal**: http://localhost:3000
   - **Editor**: http://localhost:5173
   - **Core API**: http://localhost:8000

### Option 2: Using Scripts (Easiest)

**Windows:**
```cmd
.\scripts\start-agents.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/start-agents.sh
./scripts/start-agents.sh
```

### Option 3: Using Makefile

```bash
# Initialize and start everything
make setup

# Or step by step
make init    # Create .env file
make build   # Build images
make up      # Start agents

# View logs
make logs

# Check status
make status
```

### Option 4: Manual Docker Compose

```bash
# 1. Setup environment
cp .env.agents.example .env.agents
# Edit .env.agents and add your ANTHROPIC_API_KEY

# 2. Build and start
docker-compose -f docker-compose.agents.yml --env-file .env.agents up -d

# 3. Verify
curl http://localhost:8080/health
```

## 🌐 Access Points

- **Orchestrator API:** http://localhost:8080
- **API Docs:** http://localhost:8080/docs
- **Agent Dashboard:** http://localhost:8090

## 📋 Project Structure

```
HyperCode-V2.0/
├── agents/
│   ├── base-agent/              # Shared base class
│   ├── crew-orchestrator/       # Central coordinator
│   ├── 01-frontend-specialist/  # Individual agents
│   ├── 02-backend-specialist/
│   ├── 03-database-architect/
│   ├── 04-qa-engineer/
│   ├── 05-devops-engineer/
│   ├── 06-security-engineer/
│   ├── 07-system-architect/
│   ├── 08-project-strategist/
│   ├── dashboard/               # Web UI
│   └── README.md
│
├── Configuration_Kit/           # Hive Mind (mounted)
│   ├── Team_Memory_Standards.md
│   ├── Agent_Skills_Library.md
│   └── [Agent configs...]
│
├── scripts/
│   ├── start-agents.sh          # Linux/Mac script
│   └── start-agents.bat         # Windows script
│
├── tests/
│   ├── test_agent_crew.py
│   └── requirements.txt
│
├── examples/
│   ├── api_usage.py             # Example API calls
│   └── requirements.txt
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml            # GitHub Actions
│
├── docker-compose.agents.yml    # Main compose file
├── .env.agents.example          # Environment template
├── Makefile                     # Easy commands
├── QUICKSTART.md
└── AGENT_CREW_SETUP.md         # This file
```

## 🎯 Usage Examples

### 1. Plan a Feature
```bash
curl -X POST http://localhost:8080/plan \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a shopping cart with checkout",
    "context": {"tech_stack": "Next.js, FastAPI, PostgreSQL"}
  }'
```

### 2. Check Agent Status
```bash
curl http://localhost:8080/agents/status
```

### 3. Execute with Specific Agent
```bash
curl -X POST http://localhost:8080/agent/frontend-specialist/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "frontend-specialist",
    "message": "Create a responsive product card",
    "context": {}
  }'
```

### 4. Run a Workflow
```bash
curl -X POST http://localhost:8080/workflow/feature \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "feature",
    "description": "User authentication system"
  }'
```

## 🔧 Configuration

### Environment Variables (.env.agents)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Database
POSTGRES_PASSWORD=your_password
POSTGRES_DB=hypercode
POSTGRES_USER=postgres

# Redis
REDIS_URL=redis://redis:6379

# Optional: Override models
STRATEGIST_MODEL=claude-3-opus-20240229
SPECIALIST_MODEL=claude-3-5-sonnet-20241022
```

### Resource Limits

Each agent has predefined limits in `docker-compose.agents.yml`:
- **Tier 1 (Strategist, Architect):** 0.75 CPU, 768MB RAM
- **Tier 2 (Specialists):** 0.5 CPU, 512MB RAM
- **Orchestrator:** 1 CPU, 1GB RAM

## 🧪 Testing

```bash
# Run test suite
cd tests
pip install -r requirements.txt
pytest test_agent_crew.py -v

# Or use examples
cd examples
pip install -r requirements.txt
python api_usage.py
```

## 📊 Monitoring

### View Logs
```bash
# All agents
make logs

# Specific agent
make logs-frontend
make logs-backend
```

### Check Health
```bash
# Via Makefile
make status

# Or direct curl
curl http://localhost:8080/health
curl http://localhost:8080/agents/status
```

### Dashboard
Open http://localhost:8090 in your browser

## 🛠️ Common Operations

### Restart an Agent
```bash
make restart-frontend
# Or
docker-compose -f docker-compose.agents.yml restart frontend-specialist
```

### Scale Agents
```bash
docker-compose -f docker-compose.agents.yml up -d --scale backend-specialist=3
```

### Update Agent Code
```bash
# Edit agent code, then:
make build
make restart-backend
```

### Clean Up
```bash
make clean
# Or
docker compose -f docker-compose.yml down -v
```

## 🚢 Production Deployment

See `docs/DEPLOYMENT.md` for:
- Kubernetes deployment
- Cloud platform guides (AWS, GCP, Azure)
- Security hardening
- Monitoring setup (Prometheus, Grafana)
- Backup & recovery

## 🔐 Security

1. **Never commit `.env.agents`** - Contains API keys
2. **Use secrets management** in production
3. **Regular security scans:** `make security-scan` (if configured)
4. **Update dependencies** regularly
5. **Network isolation** - Only expose orchestrator

## 🐛 Troubleshooting

### Port Conflicts
Edit `docker-compose.yml` and change port mappings

### API Key Issues
```bash
# Verify key is set
docker exec project-strategist env | grep ANTHROPIC
```

### Agent Not Responding
```bash
# Check logs
docker logs project-strategist

# Restart
docker restart project-strategist
```

### Out of Memory
```bash
# Check usage
docker stats

# Increase Docker Desktop memory limit
# Settings > Resources > Memory
```

## 📚 Additional Resources

- **Architecture:** `docs/ARCHITECTURE.md`
- **Deployment:** `docs/DEPLOYMENT.md`
- **Agent Details:** `agents/README.md`
- **Quick Start:** `QUICKSTART.md`

## 🎓 Next Steps

1. ✅ Start agents: `make up`
2. ✅ Test API: `curl http://localhost:8080/health`
3. ✅ Try examples: `python examples/api_usage.py`
4. ✅ View dashboard: http://localhost:8090
5. ✅ Plan your first feature!

## 💬 Integration with Trae

Mount your Trae workspace in `docker-compose.agents.yml`:

```yaml
volumes:
  - ${TRAE_WORKSPACE_PATH}:/workspace:ro
```

Configure MCP tools:
```yaml
environment:
  - TRAE_MCP_ENABLED=true
  - MCP_GITHUB_TOKEN=${GITHUB_TOKEN}
```

---

**Built for HyperCode V2.0** 🚀
**8 AI Agents, One Powerful Team** 🤖
