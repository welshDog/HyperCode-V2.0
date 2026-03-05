# HyperCode V2.0 Kubernetes Deployment Guide

This guide provides step-by-step instructions for deploying the HyperCode V2.0 platform to a Kubernetes cluster.

## 📋 Prerequisites

- A Kubernetes cluster (v1.24+)
- `kubectl` configured to access your cluster
- A container registry (Docker Hub, AWS ECR, etc.) to host your images
- A domain name (for Ingress configuration)

## 🚀 Deployment Steps

### 1. Namespace & Configuration

Create the isolated namespace and apply base configurations:

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmaps.yaml
```

### 2. Secrets Management

**⚠️ CRITICAL:** Before applying secrets, edit `k8s/02-secrets.yaml` and replace placeholder values with your actual production credentials.

```bash
# Edit secrets first!
# notepad k8s/02-secrets.yaml
kubectl apply -f k8s/02-secrets.yaml
```

### 3. Persistent Storage

Provision storage for stateful services (PostgreSQL, Redis, MinIO, etc.):

```bash
kubectl apply -f k8s/03-pvcs.yaml
```

### 4. Infrastructure Services

Deploy the core databases and message brokers:

```bash
kubectl apply -f k8s/04-postgres.yaml
kubectl apply -f k8s/05-redis.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n hypercode --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n hypercode --timeout=300s
```

### 5. Core Application

Deploy the main API and background workers:

```bash
kubectl apply -f k8s/06-hypercode-core.yaml
```

### 6. Observability Stack

Deploy Prometheus, Grafana, Tempo, and Loki:

```bash
kubectl apply -f k8s/07-observability.yaml
kubectl apply -f k8s/08-logging-tracing.yaml
```

### 7. Data Services

Deploy MinIO, ChromaDB, and Ollama:

```bash
kubectl apply -f k8s/09-data-services.yaml
```

### 8. Frontend Dashboard

Deploy the Next.js dashboard:

```bash
kubectl apply -f k8s/10-dashboard.yaml
```

### 9. Ingress & Networking

Expose services to the outside world:

**Note:** Update `k8s/11-ingress-network-policy.yaml` with your actual domain names before applying.

```bash
kubectl apply -f k8s/11-ingress-network-policy.yaml
```

### 10. BROski Bot

Deploy the Discord bot:

```bash
kubectl apply -f k8s/12-broski-bot.yaml
```

## 🔍 Verification

Check the status of all pods:

```bash
kubectl get pods -n hypercode
```

All pods should eventually show `Running` or `Completed`.

## 🛠️ Troubleshooting

**View logs for a specific service:**
```bash
kubectl logs -l app=hypercode-core -n hypercode
```

**Access a service locally (Port Forwarding):**
```bash
# Access Dashboard at http://localhost:3000
kubectl port-forward svc/dashboard 3000:3000 -n hypercode

# Access Grafana at http://localhost:3001
kubectl port-forward svc/grafana 3001:3000 -n hypercode
```

**Restart a deployment:**
```bash
kubectl rollout restart deployment/hypercode-core -n hypercode
```

## 📈 Scaling

Scale the core API manually:
```bash
kubectl scale deployment/hypercode-core --replicas=5 -n hypercode
```

Horizontal Pod Autoscaling (HPA) is already configured in `11-ingress-network-policy.yaml` to scale based on CPU usage.
