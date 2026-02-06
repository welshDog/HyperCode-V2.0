# 🚀 Production Deployment Guide

## Prerequisites

- Docker & Docker Compose (or Kubernetes)
- 4GB+ RAM available
- Anthropic API key
- Domain name (optional, for HTTPS)

## Deployment Options

### Option 1: Docker Compose (Recommended for Start)

#### 1. Prepare Environment
```bash
# Clone repository
git clone <your-repo>
cd HyperCode-V2.0

# Create production env file
cp .env.agents.example .env.agents.prod
nano .env.agents.prod
```

#### 2. Configure Production Settings
```bash
# .env.agents.prod
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Database
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=hypercode_prod
POSTGRES_USER=hypercode

# Security
JWT_SECRET=<random-64-char-string>
ALLOWED_ORIGINS=https://yourdomain.com

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=<optional>
```

#### 3. Deploy
```bash
# Build
docker-compose -f docker-compose.agents.yml --env-file .env.agents.prod build

# Start
docker-compose -f docker-compose.agents.yml --env-file .env.agents.prod up -d

# Verify
docker-compose -f docker-compose.agents.yml ps
curl http://localhost:8080/health
```

#### 4. Setup Reverse Proxy (nginx)
```nginx
# /etc/nginx/sites-available/hypercode-agents
server {
    listen 80;
    server_name agents.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable and reload
sudo ln -s /etc/nginx/sites-available/hypercode-agents /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d agents.yourdomain.com
```

### Option 2: Kubernetes (Production Scale)

#### 1. Create Namespace
```bash
kubectl create namespace hypercode-agents
```

#### 2. Create Secrets
```bash
kubectl create secret generic anthropic-key \
  --from-literal=api-key=sk-ant-xxxxx \
  -n hypercode-agents

kubectl create secret generic db-credentials \
  --from-literal=password=<strong-password> \
  -n hypercode-agents
```

#### 3. Deploy Infrastructure
```bash
# Apply base infrastructure
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/postgres.yaml
```

#### 4. Deploy Agents
```bash
# Apply agent deployments
kubectl apply -f k8s/orchestrator.yaml
kubectl apply -f k8s/agents/
```

#### 5. Setup Ingress
```bash
kubectl apply -f k8s/ingress.yaml
```

### Option 3: Cloud Platforms

#### AWS ECS
```bash
# Build and push images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker-compose -f docker-compose.agents.yml build
docker-compose -f docker-compose.agents.yml push

# Deploy with ECS CLI
ecs-cli compose -f docker-compose.agents.yml service up
```

#### Google Cloud Run
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/hypercode-orchestrator ./agents/crew-orchestrator

# Deploy
gcloud run deploy hypercode-orchestrator \
  --image gcr.io/PROJECT_ID/hypercode-orchestrator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances
```bash
az container create \
  --resource-group hypercode \
  --name hypercode-agents \
  --file docker-compose.agents.yml
```

## Security Hardening

### 1. API Key Rotation
```bash
# Update secrets
kubectl create secret generic anthropic-key \
  --from-literal=api-key=sk-ant-new-key \
  --dry-run=client -o yaml | kubectl apply -f -

# Rolling restart
kubectl rollout restart deployment -n hypercode-agents
```

### 2. Network Policies
```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agent-network-policy
spec:
  podSelector:
    matchLabels:
      app: agent
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: orchestrator
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
```

### 3. Resource Limits
```yaml
resources:
  limits:
    cpu: "1"
    memory: "1Gi"
  requests:
    cpu: "500m"
    memory: "512Mi"
```

### 4. Security Scanning
```bash
# Scan images for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image hypercode-orchestrator:latest
```

## Monitoring Setup

### Prometheus + Grafana
```bash
# Install Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace

# Add ServiceMonitor for agents
kubectl apply -f k8s/monitoring/service-monitor.yaml
```

### Logging (ELK Stack)
```bash
# Install Elastic
helm install elasticsearch elastic/elasticsearch -n logging --create-namespace
helm install kibana elastic/kibana -n logging

# Install Filebeat for log collection
kubectl apply -f k8s/logging/filebeat.yaml
```

### Alerting
```yaml
# prometheus-alerts.yaml
groups:
- name: agent-alerts
  rules:
  - alert: AgentDown
    expr: up{job="agent"} == 0
    for: 5m
    annotations:
      summary: "Agent {{ $labels.instance }} is down"
```

## Backup & Recovery

### Database Backup
```bash
# Automated PostgreSQL backups
kubectl create cronjob pg-backup \
  --image=postgres:15-alpine \
  --schedule="0 2 * * *" \
  -- /bin/sh -c "pg_dump -h postgres -U hypercode hypercode_prod | gzip > /backups/backup-$(date +%Y%m%d).sql.gz"
```

### Restore
```bash
# Restore from backup
kubectl exec -it postgres-0 -- psql -U hypercode -d hypercode_prod < backup.sql
```

## Performance Tuning

### 1. Redis Optimization
```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### 2. PostgreSQL Tuning
```conf
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
work_mem = 4MB
```

### 3. Agent Scaling
```yaml
# Horizontal Pod Autoscaler
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

## Health Monitoring

### Uptime Monitoring
```bash
# Use external service like:
# - Pingdom
# - UptimeRobot
# - StatusCake

# Or self-hosted
docker run -d \
  --name uptime-kuma \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  louislam/uptime-kuma:1
```

### Synthetic Testing
```python
# synthetic-test.py
import httpx
import time

def test_orchestrator():
    response = httpx.post(
        "https://agents.yourdomain.com/plan",
        json={"task": "health check test"}
    )
    assert response.status_code == 200
    
if __name__ == "__main__":
    while True:
        try:
            test_orchestrator()
            print("✅ Health check passed")
        except:
            print("❌ Health check failed")
        time.sleep(300)  # Every 5 minutes
```

## Troubleshooting

### Agent Not Responding
```bash
# Check logs
kubectl logs -f deployment/backend-specialist -n hypercode-agents

# Restart agent
kubectl rollout restart deployment/backend-specialist -n hypercode-agents

# Check resource usage
kubectl top pods -n hypercode-agents
```

### High Latency
```bash
# Check Redis
redis-cli --latency

# Check PostgreSQL connections
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check network
kubectl exec -it orchestrator-pod -- ping redis
```

### Out of Memory
```bash
# Increase limits
kubectl patch deployment backend-specialist -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend-specialist","resources":{"limits":{"memory":"2Gi"}}}]}}}}'
```

## Cost Optimization

### 1. API Usage Monitoring
```python
# Track Anthropic API costs
import anthropic

client = anthropic.Anthropic()
usage = client.messages.count_tokens(
    model="claude-3-5-sonnet-20241022",
    messages=[...]
)
cost = usage.input_tokens * 0.003 / 1000  # $3 per MTok
```

### 2. Spot Instances (AWS/GCP)
```yaml
# Use spot instances for non-critical agents
nodeSelector:
  node.kubernetes.io/instance-type: spot
```

### 3. Caching Strategy
- Cache LLM responses for common tasks
- Use Redis for session data
- CDN for static assets

## Maintenance

### Regular Updates
```bash
# Update base images monthly
docker-compose -f docker-compose.agents.yml pull
docker-compose -f docker-compose.agents.yml up -d

# Update dependencies
pip-compile requirements.in
docker-compose -f docker-compose.agents.yml build
```

### Health Checks
- Weekly: Review error logs
- Monthly: Security scan, dependency updates
- Quarterly: Load testing, capacity planning

---

**Support**: For issues, create a GitHub issue or contact the team.
**Documentation**: See `docs/` for detailed guides.
