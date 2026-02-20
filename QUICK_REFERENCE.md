# Quick Reference Card - HyperCode Orchestration

## 🚀 START SERVICES

### Development
```powershell
.\hypercode.ps1 start
```
**Result**: All core services up in ~2 minutes

### Production
```powershell
$env:ENVIRONMENT="production"
.\hypercode.ps1 start
```

### With Agents
```powershell
.\hypercode.ps1 agents
```

### Windows Quick-Start
```cmd
start.bat dev
start.bat prod
start.bat agents
```

---

## 📊 MONITOR HEALTH

```bash
# Real-time dashboard (recommended)
python scripts/health-monitor.py --live

# One-time check
python scripts/health-monitor.py
```

**Output Shows**:
- Service name | Status | Response time (ms) | Docker status
- Green ✓ = healthy
- Red ✗ = timeout/error
- Yellow ⚠ = skipped/warning

---

## 📋 SHOW STATUS

```powershell
.\hypercode.ps1 status
```

**Output**:
- Container status (running/unhealthy/exited)
- Running count | Unhealthy count | Exited count
- Color-coded for quick scanning

---

## 📝 VIEW LOGS

```powershell
# All services
.\hypercode.ps1 logs

# Specific service
.\hypercode.ps1 logs frontend-specialist
.\hypercode.ps1 logs hypercode-core
.\hypercode.ps1 logs security-engineer

# Using docker-compose directly
docker-compose -f docker-compose.yml logs hypercode-core
docker-compose -f docker-compose.yml logs -f postgres
```

---

## 🔄 RESTART SERVICES

```powershell
# Everything
.\hypercode.ps1 restart

# Specific container
docker-compose -f docker-compose.yml restart frontend-specialist

# Force stop and start
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml up -d
```

---

## 🛑 STOP SERVICES

```powershell
.\hypercode.ps1 stop

# Or
docker-compose -f docker-compose.yml down
```

---

## 🧹 CLEANUP

```powershell
# Full cleanup (removes dangling images, containers, volumes)
.\hypercode.ps1 clean

# Just see what will be removed
docker system df

# Manual cleanup options
docker system prune -a           # Remove all unused
docker system prune -a --volumes # Also remove volumes
docker image prune -a            # Just images
docker volume prune              # Just volumes
```

---

## 🐛 TROUBLESHOOTING

### Services won't start
```powershell
# 1. Check if .env file exists
Test-Path .env

# 2. Try full cleanup
.\hypercode.ps1 clean

# 3. Restart from scratch
.\hypercode.ps1 start

# 4. Monitor in real-time
python scripts/health-monitor.py --live
```

### Memory issues (OOM)
```bash
# Check current usage
docker stats

# Look for high memory containers
docker stats --no-stream

# Restart just that service
docker-compose -f docker-compose.yml restart redis
```

### Specific agent unhealthy
```powershell
# View its logs
.\hypercode.ps1 logs frontend-specialist

# Check if dependencies are healthy
.\hypercode.ps1 status

# Restart just that agent
docker-compose -f docker-compose.yml restart frontend-specialist

# Test manually
docker exec frontend-specialist curl http://localhost:8002/health
```

### Disk full
```bash
# See what's using space
docker system df

# Clean up old data
docker system prune -a --volumes --force

# Check sizes
du -sh *  # Linux/Mac
dir       # Windows
```

---

## 🌐 ACCESS SERVICES

After starting, visit:

| Service | URL | Purpose |
|---------|-----|---------|
| Dashboard | http://localhost:8088 | Nginx dashboard |
| Terminal | http://localhost:3000 | Next.js terminal |
| Editor | http://localhost:5173 | Vite editor |
| Grafana | http://localhost:3001 | Monitoring/dashboards |
| Prometheus | http://127.0.0.1:9090 | Metrics DB |
| Jaeger | http://localhost:16686 | Distributed tracing |
| Core API | http://localhost:8000 | HyperCode core |
| Orchestrator | http://127.0.0.1:8080 | Agent orchestrator |
| Ollama | http://127.0.0.1:11434 | LLM models |

---

## 🔐 ENVIRONMENT VARIABLES

Required (.env file):
```bash
POSTGRES_PASSWORD=<strong-password>
GF_SECURITY_ADMIN_PASSWORD=<strong-password>
OPENAI_API_KEY=sk-...
```

Optional (.env file):
```bash
ENVIRONMENT=development  # or production
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
```

---

## 📈 SERVICE PROFILES

### Core (always starts)
- hypercode-core
- broski-terminal
- hyperflow-editor
- celery-worker
- redis
- postgres
- prometheus
- grafana
- jaeger
- ollama
- hafs-service
- dashboard

### Agents (opt-in with `--profile agents`)
- crew-orchestrator
- frontend-specialist
- backend-specialist
- database-architect
- qa-engineer
- devops-engineer
- security-engineer
- system-architect
- project-strategist

---

## ⚡ PERFORMANCE TARGETS

After optimization:
- **Startup time**: <2 minutes
- **Health check time**: <5 seconds
- **Memory stable**: >24 hours
- **Zero false positives**: Health accurate
- **Build incremental**: <60 seconds

If not meeting targets:
1. Run `.\hypercode.ps1 clean` and restart
2. Check `python scripts/health-monitor.py --live`
3. View logs for errors
4. Verify .env is set correctly

---

## 🆘 GET HELP

```powershell
# Read the full guide
code ORCHESTRATION_GUIDE.md

# See what changed
code OPTIMIZATION_SUMMARY.md
code CHANGELOG.md

# Monitor services
python scripts/health-monitor.py --live

# View specific logs
.\hypercode.ps1 logs [service-name]

# Check Docker daemon
docker version
docker ps -a
```

---

## 📱 One-Liners

```powershell
# Full reset
.\hypercode.ps1 clean; .\hypercode.ps1 start; python scripts/health-monitor.py --live

# Dev workflow
.\hypercode.ps1 start; python scripts/health-monitor.py --live

# Check everything
.\hypercode.ps1 status

# View all logs
.\hypercode.ps1 logs

# Quick test
docker ps -a && echo "Docker OK"
```

---

**Last Updated**: Feb 20, 2026
**Status**: Production Ready ✅
