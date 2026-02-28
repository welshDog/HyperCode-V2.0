# Troubleshooting Guide

## Common Issues

### 1. "Backend offline?" / Connection Error
**Symptom**: The CLI says it can't connect to `localhost:8000`.
**Fix**:
1.  Check if Docker is running: `docker ps`.
2.  If `hypercode-core` is missing or exited, check logs:
    ```bash
    docker logs hypercode-core
    ```
3.  Ensure port 8000 isn't used by another app.

### 2. Task stuck in "Pending"
**Symptom**: CLI says "Task Queued" but no output file appears.
**Fix**:
1.  Check the worker logs:
    ```bash
    docker logs -f celery-worker
    ```
2.  If you see "Connection refused" to Redis, ensure Redis is up.
3.  If you see "No route found", check `backend/app/agents/router.py` to ensure your task type maps to an agent.

### 3. Pulse Agent says "CRITICAL: Cannot reach Prometheus"
**Symptom**: `hypercode pulse` returns a critical error.
**Fix**:
1.  The Pulse Agent runs *inside* Docker. It tries to reach `http://prometheus:9090`.
2.  Ensure the `prometheus` service is running in `docker-compose.yml`.
3.  Check if they are on the same Docker network (`backend-net`).

### 4. Git Merge Conflicts
**Symptom**: `git status` shows "Unmerged paths".
**Fix**:
1.  Open the file in VS Code.
2.  Look for `<<<<<<< HEAD`.
3.  Choose "Accept Incoming Change" (or whichever is correct).
4.  `git add .`
5.  `git commit`.

### 5. CLI "Missing auth token"
**Symptom**: CLI refuses to run.
**Fix**:
1.  Create a file named `token.txt` in the root directory.
2.  Paste a valid JWT access token from the backend login (or ask a senior dev/admin for one).
