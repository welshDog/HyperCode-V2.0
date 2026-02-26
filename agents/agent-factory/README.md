# Hyper Agent Factory - Service Manifest

## Overview
This service acts as the **central spawner** for the HyperCode swarm. It manages the lifecycle of all dynamic agents.

## Deployment
To deploy this service, build the Docker image and run it on port 9000.

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## Configuration
- **Port**: 9000 (Internal)
- **Dependencies**: `fastapi`, `uvicorn`, `redis` (future), `docker` (future)

## Roadmap
1. **Docker Integration**: Use `docker-py` to actually spin up containers from blueprints.
2. **Redis State**: Move the in-memory `REGISTRY` to Redis for persistence.
3. **Health Monitoring**: Implement a background task loop to check `/health` on all spawned agents.
