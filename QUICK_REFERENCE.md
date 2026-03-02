# QUICK REFERENCE GUIDE
**Docker Environment:** HyperCode V2.0  
**Last Updated:** 2026-03-01 23:00 UTC

---

## 🚀 QUICK START COMMANDS

### Check Status
```bash
# All containers
docker ps -a

# Health status detailed
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.State}}"

# System resources
docker stats --no-stream

# Disk usage
docker system df
```

### View Logs
```bash
# Real-time logs
docker logs -f <container_name>

# Last 50 lines
docker logs --tail 50 <container_name>

# Specific time range
docker logs --since 1h <container_name>

# Critical services
docker logs -f hypercode-core
docker logs -f postgres
docker logs -f redis
```

### Restart Services
```bash
# Single service
docker restart <container_name>

# All services
docker compose restart

# Monitoring stack
docker compose restart prometheus grafana loki tempo

# Specific service
docker compose restart hypercode-core
```

### Execute Commands
```bash
# Bash in container
docker exec -it <container_name> bash

# Run command
docker exec <container_name> <command>

# PostgreSQL queries
docker exec -it postgres psql -U postgres -d hypercode -c "SELECT * FROM users;"

# Redis commands
docker exec -it redis redis-cli
docker exec -it redis redis-cli INFO

# Check Ollama models
docker exec -it hypercode-ollama ollama list
```

---

## 🔌 SERVICE ENDPOINTS

### User-Facing Services
| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Dashboard** | http://localhost:8088 | None needed | Web UI |
| **Grafana** | http://localhost:3001 | admin/admin | Monitoring |
| **MinIO Console** | http://localhost:9001 | minioadmin/minioadmin | File storage |
| **Prometheus** | http://localhost:9090 | None needed | Metrics |

### API Endpoints (Internal)
| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| **HyperCode Core** | http://hypercode-core:8000 | 8000 | Main API |
| **ChromaDB** | http://chroma:8000 | 8009 | Vector search |
| **Ollama** | http://ollama:11434 | 11434 | LLM |
| **PostgreSQL** | postgres:5432 | 5432 | Database |
| **Redis** | redis:6379 | 6379 | Cache |
| **Loki** | http://loki:3100 | 3100 | Logs |
| **Tempo** | http://tempo:3200 | 3200 | Traces |

---

## 📊 WHAT'S RUNNING

### Core System (5 services)
- ✅ **hypercode-core** - Main API server
- ✅ **PostgreSQL** - Database (port 5432)
- ✅ **Redis** - Cache (port 6379)
- ✅ **ChromaDB** - Vector DB (port 8009)
- ✅ **Ollama** - LLM service (port 11434)

### Processing (2 services)
- ✅ **Celery Worker** - Job processing
- ✅ **Crew Orchestrator** - Agent management

### AI Agents (9 services)
- ✅ **Coder Agent** - Code generation
- ✅ **Frontend Specialist** - UI/UX
- ✅ **Backend Specialist** - Server logic
- ✅ **Database Architect** - Schema design
- ✅ **QA Engineer** - Testing
- ✅ **DevOps Engineer** - Infrastructure
- ✅ **Security Engineer** - Security review
- ✅ **System Architect** - Architecture
- ✅ **Project Strategist** - Planning

### Storage (2 services)
- ✅ **MinIO** - S3 storage (port 9000/9001)
- ✅ **PostgreSQL** - Primary database

### Monitoring (7 services)
- ✅ **Prometheus** - Metrics (port 9090)
- ✅ **Grafana** - Dashboards (port 3001)
- ✅ **Node Exporter** - System metrics
- ✅ **cAdvisor** - Container metrics
- ✅ **Loki** - Log aggregation
- ✅ **Tempo** - Distributed tracing
- ✅ **Promtail** - Log shipper

### UI (1 service)
- ✅ **Dashboard** - Web interface (port 8088)

---

## 🔐 DEFAULT CREDENTIALS (⚠️ CHANGE IN PRODUCTION)

| Service | Username | Password | Location |
|---------|----------|----------|----------|
| PostgreSQL | postgres | changeme | Port 5432 |
| MinIO | minioadmin | minioadmin | Port 9001 |
| Grafana | admin | admin | Port 3001 |

### Change Credentials
```bash
# PostgreSQL
docker exec -it postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'new_password';"

# Update docker-compose.yml: POSTGRES_PASSWORD=new_password
# Restart: docker compose restart postgres

# MinIO
# Edit MINIO_ROOT_PASSWORD in docker-compose.yml
# Restart: docker compose restart minio

# Grafana
# UI → Administration → Users → admin → Change password
```

---

## 🐛 TROUBLESHOOTING

### Container Won't Start
```bash
# Check logs
docker logs <container_name>

# Check resource limits
docker inspect <container_name> --format='{{.HostConfig.Memory}}'

# Check port conflicts
docker ps | grep <port>
```

### Database Connection Issues
```bash
# Test PostgreSQL
docker exec -it postgres pg_isready -U postgres

# Test Redis
docker exec -it redis redis-cli ping

# Check logs
docker logs postgres
docker logs redis
```

### Monitoring Issues
```bash
# Test Prometheus scrape
docker exec -it prometheus wget -O- http://prometheus:9090/api/v1/targets

# Test Grafana datasource
curl http://localhost:3001/api/datasources

# Check Loki readiness
docker exec -it loki curl http://localhost:3100/ready
```

### Agent Issues
```bash
# Check agent logs
docker logs project-strategist

# Test agent health
curl http://localhost:8001/health

# Check core API
curl http://hypercode-core:8000/health
```

---

## 📈 MONITORING DASHBOARD

### Access Monitoring
1. Open Grafana: http://localhost:3001
2. Login: admin/admin
3. Select dashboard from dropdown

### Key Metrics
- CPU Usage: Should be <5% average
- Memory: Should be <75% utilized
- Disk: Monitor free space (should be >20% available)
- Request Latency: Should be <200ms (95th percentile)

### Create Alert
1. Grafana → Alerts → Create Alert Rule
2. Choose metric (e.g., CPU > 80%)
3. Set notification channel (Discord configured)
4. Save

---

## 🔄 BACKUP & RESTORE

### Backup Critical Data
```bash
# Backup PostgreSQL
docker exec postgres pg_dump -U postgres hypercode > backup.sql

# Backup Redis
docker exec redis redis-cli BGSAVE
docker cp redis:/data/dump.rdb ./redis_backup.rdb

# Backup volumes
docker run --rm -v hypercode-v20_postgres-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

### Restore Data
```bash
# Restore PostgreSQL
cat backup.sql | docker exec -i postgres psql -U postgres -d hypercode

# Restore Redis
docker cp redis_backup.rdb redis:/data/
docker exec redis redis-cli SHUTDOWN
docker restart redis
```

---

## 🔧 COMMON TASKS

### View Container Resource Usage
```bash
docker stats --no-stream

# Specific container
docker stats --no-stream postgres
```

### Update Image
```bash
# Pull latest
docker pull hypercode-v20-dashboard

# Rebuild local image
docker compose build hypercode-dashboard

# Restart service
docker compose up -d hypercode-dashboard
```

### Access Container Filesystem
```bash
# Copy from container
docker cp hypercode-core:/app/outputs/file.txt ./

# Copy to container
docker cp ./file.txt hypercode-core:/app/
```

### View Environment Variables
```bash
docker exec <container_name> env

# Specific variable
docker exec <container_name> env | grep POSTGRES
```

### Check Network Connectivity
```bash
# From container to another service
docker exec hypercode-core curl http://postgres:5432

# Check DNS resolution
docker exec hypercode-core nslookup postgres
```

---

## 🚨 ALERT THRESHOLDS

### Memory
- ⚠️ Warning: >75% utilized
- 🔴 Critical: >90% utilized

### CPU
- ⚠️ Warning: >5% average
- 🔴 Critical: >10% average

### Disk
- ⚠️ Warning: <20% available
- 🔴 Critical: <10% available

### Response Time
- ⚠️ Warning: >200ms (95th percentile)
- 🔴 Critical: >500ms (95th percentile)

### Container Health
- ⚠️ Warning: Unhealthy for >2 minutes
- 🔴 Critical: Exited or restarting

---

## 📞 SUPPORT

### Check System Health
```bash
# Full status report
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.State}}"
docker system df
docker ps --format "{{.Names}}" | xargs -I {} docker exec {} curl -s http://localhost:8001/health
```

### Collect Diagnostic Info
```bash
# Docker daemon logs
docker ps -a > docker_status.txt
docker images >> docker_status.txt
docker system df >> docker_status.txt
docker ps --format "table {{.Names}}\t{{.Status}}" >> docker_status.txt

# Container logs
docker logs prometheus > prometheus.log
docker logs grafana > grafana.log
docker logs hypercode-core > hypercode-core.log
```

### Emergency Restart
```bash
# Restart everything
docker compose restart

# Restart with full cleanup
docker compose down
docker compose up -d
```

---

## 🎓 LEARNING RESOURCES

### Docker Commands
- `docker ps` - List containers
- `docker logs` - View container logs
- `docker exec` - Run command in container
- `docker stats` - Monitor resources
- `docker restart` - Restart container

### Useful Queries
```sql
-- PostgreSQL: Check tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- PostgreSQL: Check users
SELECT usename, usesuper, usecreatedb FROM pg_user;

-- Redis: Check memory
INFO memory
```

### Monitoring Queries
```
# Prometheus: CPU usage
rate(container_cpu_usage_seconds_total[5m])

# Prometheus: Memory usage
container_memory_usage_bytes / 1024 / 1024

# Prometheus: Request latency
http_request_duration_seconds_bucket
```

---

## 📋 FILE LOCATIONS

### Important Files
- `docker-compose.yml` - Container definitions
- `.env.example` - Environment template
- `./monitoring/` - Monitoring configs
- `./backend/` - Backend source code
- `./agents/` - AI agent implementations
- `./dashboard/` - Frontend code

### Volumes Location
- PostgreSQL: `./docker_volumes/postgres-data`
- Redis: `./docker_volumes/redis-data`
- Prometheus: `./docker_volumes/prometheus-data`
- Grafana: `./docker_volumes/grafana-data`
- MinIO: `./docker_volumes/minio-data`

---

## ✅ DAILY CHECKLIST

- [ ] All containers running: `docker ps | wc -l`
- [ ] No error logs: `docker logs postgres | grep ERROR`
- [ ] Disk space available: `docker system df`
- [ ] Monitoring accessible: http://localhost:3001
- [ ] API responding: `curl http://localhost:8088`
- [ ] Database healthy: `docker exec postgres pg_isready`
- [ ] Cache healthy: `docker exec redis redis-cli ping`

---

**Keep this guide handy for quick reference!**
