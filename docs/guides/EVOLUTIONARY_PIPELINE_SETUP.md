# HyperCode Evolutionary Pipeline (H.E.P.) - Implementation Guide

**Version:** 1.0.0  
**Status:** Planning  
**Target:** Enable Agent Self-Evolution and Automated DevOps

## 1. Project Overview
The **HyperCode Evolutionary Pipeline** allows specialized agents to propose, implement, test, and deploy improvements to their own codebase or other agents' codebases. This creates a closed-loop system for continuous self-improvement.

## 2. Detailed Prerequisites

Before the pipeline can function, the **DevOps Engineer Agent** must be elevated to a "privileged" status to control the Docker daemon.

### 2.1. Docker Access (Crucial)
The `devops-engineer` container currently runs in a hardened state. To enable deployments, we must:
1.  **Install Docker CLI**: The agent needs the `docker` binary to execute commands.
2.  **Mount Socket**: The host's `/var/run/docker.sock` must be exposed to the container.

### 2.2. Technologies
-   **Docker & Docker Compose**: The runtime environment.
-   **Python 3.11+**: For agent logic.
-   **Redis**: For inter-agent communication (Event Bus).
-   **Git**: (Optional but recommended) For version control integration.

## 3. Initial Setup Procedures

### Step 1: Empower the DevOps Agent
**Action**: Update `agents/05-devops-engineer/Dockerfile`.
```dockerfile
# Add to Runtime Stage
RUN apt-get update && apt-get install -y docker.io
```

**Action**: Update `docker-compose.yml`.
```yaml
  devops-engineer:
    # ...
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock # RESTORED
    environment:
      - DOCKER_HOST=unix:///var/run/docker.sock # RESTORED
```

### Step 2: Create the "Deployer" Tool
Create a tool definition that the DevOps agent can use to trigger updates.
**File**: `agents/shared/tools/deployer.py`
```python
def deploy_service(service_name: str):
    """
    Rebuilds and restarts a specific service.
    """
    # 1. Build
    subprocess.run(["docker", "compose", "build", service_name], check=True)
    # 2. Up (Rolling update)
    subprocess.run(["docker", "compose", "up", "-d", "--no-deps", service_name], check=True)
```

## 4. Project Structure Guidelines

Organize the evolutionary logic within the `agents/shared` directory so all agents understand the protocol, while keeping the execution logic restricted to `devops-engineer`.

```text
agents/
├── shared/
│   ├── protocols/
│   │   └── evolution.py       # Defines the "ImprovementRequest" data structure
│   └── tools/
│       └── deployer.py        # The actual Docker wrapper (DevOps only)
```

## 5. Key Milestones (Phase 1)

| Milestone | Description | Success Metric |
| :--- | :--- | :--- |
| **M1: DevOps Awakening** | DevOps agent can run `docker ps` successfully. | `{"status": "success", "output": "CONTAINER ID..."}` |
| **M2: The Mirror Test** | DevOps agent can restart *itself* (or a dummy service). | Service uptime resets; logs show clean startup. |
| **M3: The Loop** | Coder modifies a file -> QA passes -> DevOps deploys. | Code change is reflected in the running container. |

## 6. Technical Requirements & Standards

*   **Idempotency**: Deployment scripts must handle partial failures gracefully.
*   **Rollback**: If a new container fails the health check, the system must revert to the previous image.
*   **Security**: Only the `devops-engineer` and `system-architect` should be allowed to trigger deployments.
*   **Logging**: All evolutionary events must be logged to Redis with high priority.

## 7. Testing Methodology

1.  **Sandbox Environment**: Do not test on `hypercode-core` initially. Create a `test-agent` service in `docker-compose.yml` specifically for being killed/restarted.
2.  **Mocking**: Unit test the `deployer.py` logic by mocking `subprocess.run`.
3.  **Integration**: Trigger a deployment and poll the `/health` endpoint until it returns 200.

## 8. Quality Metrics

*   **Deployment Success Rate**: Target > 95%.
*   **Recovery Time**: < 30 seconds for a service restart.
*   **False Positives**: 0 incidents of deploying broken code (QA gate must be strict).

---
**Next Step:** Execute "Step 1: Empower the DevOps Agent" to begin.
