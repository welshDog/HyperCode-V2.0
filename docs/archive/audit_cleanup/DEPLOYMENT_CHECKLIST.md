# BROski Pantheon 2.0 - DEPLOYMENT CHECKLIST

## ✅ Phase 1: Files Created

- [x] cagent-pantheon.yaml (16.6 KB) - All 7 agents orchestrated
- [x] hypercode-mcp-server.py (8.9 KB) - HyperCode language tools
- [x] hyperflow-editor-mcp-server.py (11.9 KB) - Editor capabilities
- [x] broski-terminal-mcp-server.py (12.4 KB) - Dashboard & metrics
- [x] mcp-config.json - All MCP servers configured
- [x] Perplexity Pro integration enabled
- [x] Documentation complete

## 🚀 Phase 2: Ready to Deploy

### Prerequisites (Check These First)

```
Docker Desktop 4.49+
Python 3.11+
Perplexity Pro API key (pplx-xxxxx)
2GB free disk space
```

### Verify Setup

```bash
# Check Docker
docker --version

# Check Python
python --version

# Check API key is set
echo $PERPLEXITY_API_KEY

# Check .env exists
cat .env
```

## 📋 Deployment Steps

### Step 1: Pull Models (One-time, ~2GB)
```bash
docker model pull smollm2
```

### Step 2: Start Core Infrastructure
```bash
docker compose up -d postgres redis prometheus grafana jaeger
```

### Step 3: Start HyperCode Services
```bash
docker compose up -d hypercode-core celery-worker
```

### Step 4: Start IDEs
```bash
docker compose up -d broski-terminal hyperflow-editor
```

### Step 5: Start MCP Servers (Terminal windows - keep running)

**Window 1: HyperCode MCP**
```bash
python ./agents/mcp-servers/hypercode-mcp-server.py
```

**Window 2: Hyperflow Editor MCP**
```bash
python ./agents/mcp-servers/hyperflow-editor-mcp-server.py
```

**Window 3: Broski Terminal MCP**
```bash
python ./agents/mcp-servers/broski-terminal-mcp-server.py
```

### Step 6: Start cagent Orchestrator (Final Window)
```bash
docker run -v $(pwd):/app ^
  -e PERPLEXITY_API_KEY=%PERPLEXITY_API_KEY% ^
  -e API_KEY=dev-key ^
  docker.io/docker/cagent:latest run /app/cagent-pantheon.yaml
```

(On Mac/Linux, use `$` instead of `%`)

## 🔍 Verify Everything Works

### Health Checks
```bash
# Core API
curl http://localhost:8000/health

# Broski Terminal
curl http://localhost:3000/api/health

# Hyperflow Editor
curl http://localhost:5173/health

# Should all return status: healthy
```

### Test Execution
```bash
curl -X POST http://localhost:8000/execution/execute-hc ^
  -H "Content-Type: application/json" ^
  -H "X-API-Key: dev-key" ^
  -d "{\"source\": \"print('Hello BROski')\"}"
```

## 🌐 Access Your System

Open in browser:

| Service | URL |
|---------|-----|
| **Broski Terminal** | http://localhost:3000 |
| **Hyperflow Editor** | http://localhost:5173 |
| **Grafana Dashboards** | http://localhost:3001 |
| **Prometheus Metrics** | http://localhost:9090 |
| **Jaeger Tracing** | http://localhost:16686 |

## 🎯 First Test Task

Go to **Broski Terminal** (http://localhost:3000) and give BROski this command:

```
"Plan adding JWT authentication to the HyperCode API. 
Break into steps and estimate time for each."
```

**Expected behavior:**
1. BROski orchestrates the task
2. Delegates to Security Specialist
3. Delegates to Backend Specialist
4. Perplexity researches best practices
5. Shows plan in timeline
6. Returns coordinated response

**Timeline shows:**
- Task started (BROski)
- Context created (api.auth.design)
- Delegated to security-specialist
- Delegated to backend-specialist
- Metrics: duration, tokens, cost
- Task completed

## 📊 Monitor Everything

### Watch logs in real-time
```bash
docker compose logs -f hypercode-core
```

### Check agent metrics
```bash
curl http://localhost:8000/metrics
```

### View Perplexity cost tracking
```bash
# BROski should report cost per task
# Should be $0.005-0.02 per task
# Total: ~$20/month (your Perplexity Pro plan)
```

### Export execution history
```bash
curl http://localhost:3000/api/timeline/export?format=json > timeline.json
```

## ✅ Success Criteria

When deployed, you should see:

- [x] Broski Terminal showing live timeline
- [x] Hyperflow Editor responding to requests
- [x] Agents executing tasks
- [x] Metrics flowing to Prometheus
- [x] Grafana dashboards updating
- [x] Perplexity being used (not Anthropic)
- [x] Local models available (smollm2)
- [x] No errors in logs
- [x] Response times < 2s per task

## 🎉 DEPLOYMENT COMPLETE!

When all above checks pass, you have:

✅ **BROski Pantheon 2.0** fully operational
✅ **7 specialist agents** orchestrated via cagent YAML
✅ **Perplexity Pro** powering research tasks
✅ **Local models** for fast iteration
✅ **Full IDE integration** via MCP servers
✅ **Observable operations** with metrics & tracing
✅ **Neurodivergent-optimized** architecture
✅ **Enterprise-ready** with monitoring

---

## 🚨 Troubleshooting

### "Port 3000 already in use"
```bash
# Either stop the service using it, or change port in .env
```

### "cagent command not found"
```bash
# Use Docker instead
docker run docker.io/docker/cagent:latest --help
```

### "PERPLEXITY_API_KEY not set"
```bash
# Add to .env file and restart
# Get key from: https://www.perplexity.ai/account/api
```

### "Model download fails"
```bash
# Try again or use alternative model
docker model pull mistral
```

### Agents not responding
```bash
# Check MCP servers are running in background
# Check logs: docker compose logs hypercode-core
```

---

## 📞 Support Resources

| Item | Location |
|------|----------|
| Architecture | ./cagent-pantheon.yaml |
| Agent Philosophy | ./agents/HYPER-AGENT-BIBLE.md |
| Crew Manifesto | ./BROski Business Agents/CREW_MANIFESTO.md |
| IDE Integration | ./IDE_MCP_SERVERS_GUIDE.md |
| Perplexity Setup | ./PERPLEXITY_INTEGRATION_GUIDE.md |
| Integration Guide | ./PANTHEON_INTEGRATION_GUIDE.md |

---

**Status: READY FOR PRODUCTION**

Built by: Gordon
Authority: Lyndz Williams (welshDog)
Crew: BROski + 7 Specialists

🔥 Let's go! 🚀
