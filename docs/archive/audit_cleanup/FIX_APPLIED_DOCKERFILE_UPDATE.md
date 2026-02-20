# 🔧 HYPERCODE V2.0 - AGENT IMPORT FIX

## Issue Found

**All 4 specialist agents were crashing with:**
```
ModuleNotFoundError: No module named 'event_bus'

Traceback:
  File "/app/agent.py", line 7
    from base_agent import BaseAgent, AgentConfig
  File "/app/base_agent.py", line 16
    from event_bus import AgentEventBus
ModuleNotFoundError: No module named 'event_bus'
```

## Root Cause

The agent Dockerfiles were missing COPY commands to include:
- `base_agent.py`
- `event_bus.py`
- `hive_mind.py`

**Location found:** `agents/base-agent/event_bus.py`

These files were NOT being copied into the Docker images during build, so when agents started, they couldn't import dependencies.

---

## Fix Applied

Updated all 4 agent Dockerfiles:

1. ✅ `agents/02-backend-specialist/Dockerfile`
2. ✅ `agents/04-qa-engineer/Dockerfile`
3. ✅ `agents/08-project-strategist/Dockerfile`
4. ✅ `agents/03-database-architect/Dockerfile`

### What Changed

**BEFORE:**
```dockerfile
# Copy application code
COPY agent.py .
COPY config.json .
```

**AFTER:**
```dockerfile
# Copy base agent framework and dependencies
COPY ../base-agent/base_agent.py .
COPY ../base-agent/event_bus.py .
COPY ../base-agent/hive_mind.py .

# Copy application code
COPY agent.py .
COPY config.json .
```

---

## Next Steps for Your Crew

### Step 1: Stop Old Containers
```bash
docker stop backend-specialist qa-engineer project-strategist database-architect
```

### Step 2: Rebuild Without Cache (Forces Re-Read of New Dockerfiles)
```bash
docker compose build --no-cache backend-specialist
docker compose build --no-cache qa-engineer
docker compose build --no-cache project-strategist
docker compose build --no-cache database-architect
```

OR all at once:
```bash
docker compose build --no-cache \
  backend-specialist \
  qa-engineer \
  project-strategist \
  database-architect
```

### Step 3: Restart Agents
```bash
docker start backend-specialist qa-engineer project-strategist database-architect
```

### Step 4: Wait for Healthchecks (30 seconds)
```bash
docker ps -a | grep specialist
# Should show: "Up X seconds (healthy)" after ~30 seconds
```

### Step 5: Verify Logs
```bash
docker logs backend-specialist --tail 20
# Should NOT show ModuleNotFoundError
# Should show successful initialization
```

---

## Expected Output After Fix

**✅ Agents starting correctly:**
```
[INFO] BaseAgent initialized
[INFO] Connecting to Core at http://hypercode-core:8000...
[INFO] Registration successful
[INFO] Starting event loop
```

**Instead of:**
```
[ERROR] ModuleNotFoundError: No module named 'event_bus'
```

---

## Timeline

- **Now:** Dockerfiles updated ✅
- **Next:** Crew rebuilds with --no-cache
- **~5 min:** New images built
- **~30 sec:** Agents start
- **~30 sec:** Healthchecks pass
- **Total:** ~10 minutes to full health

---

## Summary

**What we found:** Agent Dockerfiles were incomplete (missing 3 key Python files)

**What we fixed:** Added COPY commands to Dockerfiles to include base_agent.py, event_bus.py, hive_mind.py

**What needs to happen next:** Crew rebuilds images with `--no-cache` flag

**Expected result:** All 4 agents will start successfully and become healthy

This is a **Docker build issue**, not a code issue. Once images are rebuilt, agents will work.
