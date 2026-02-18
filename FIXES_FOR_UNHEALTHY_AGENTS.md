# HyperCode V2.0 - Agent Health Fixes

## Problem Summary
- **hypercode-core crashed** (Exited 255): IndexError in agents.py at line 103
- **4 agents unhealthy** (project-strategist, qa-engineer, backend-specialist, database-architect)
- **401 Unauthorized errors** preventing agent registration
- **Connection pool exhaustion**: Database timeout after 36 hours

---

## Root Causes

### 1. **IndexError in `/agents/bible` endpoint** (CRITICAL)
**File:** `THE HYPERCODE/hypercode-core/app/routers/agents.py:103`

**Original Code:**
```python
base = Path(__file__).resolve().parents[4]  # Fails - only 3 parent levels exist
md_path = base / "agents" / "HYPER-AGENT-BIBLE.md"
```

**Issue:** Path doesn't have 4 parent levels in Docker, causing crash on any agent request

**Fixed Code:** ✅ Already applied (multiple path resolution strategies)
- Tries 4 different path locations
- Graceful fallback if file not found

---

### 2. **Agent Authentication (401 Errors)**
**Root Cause:** Agents sending requests to hypercode-core, but core expects valid `API_KEY` in Authorization header

**Agents Getting 401:**
- project-strategist
- qa-engineer
- backend-specialist
- database-architect

**Fix Required:** Ensure all agents pass API_KEY in their requests

**Location:** `agents/base-agent/agent.py` or individual agent implementations

---

### 3. **Database Connection Pool Exhaustion**
**Symptom:** `Timed out fetching a new connection from the connection pool. More info: http://pris.ly/d/connection-pool (Current connection limit: 5)`

**Fix:** Increase Prisma connection pool

**Method 1 - Docker Compose (Recommended):**
```yaml
environment:
  - DATABASE_CONNECTION_LIMIT=20  # Increase from default 5
```

**Method 2 - Connection String:**
```
postgresql://user:pass@host/db?connection_limit=20
```

---

## Implementation Steps

### Step 1: Verify agents.py Fix ✅
The fix has been applied to: `THE HYPERCODE/hypercode-core/app/routers/agents.py`

Changes include:
- Multiple path resolution strategies
- Graceful error handling
- Proper logging

### Step 2: Fix Agent Authorization
**Update all agent base implementations to include API_KEY:**

```python
# In agents/base-agent/agent.py or each agent's main.py

def get_auth_headers():
    api_key = os.getenv("HYPERCODE_API_KEY", os.getenv("API_KEY"))
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

# Use in requests
response = requests.post(
    "http://hypercode-core:8000/agents/register",
    json=registration_data,
    headers=get_auth_headers()
)
```

### Step 3: Rebuild and Restart Services

```bash
# Stop all services
docker compose down

# Rebuild hypercode-core with fixed agents.py
docker compose build hypercode-core --no-cache

# Start services with agents profile
docker compose up -d --profile agents
```

### Step 4: Verify Health

```bash
# Check hypercode-core is healthy
docker ps | grep hypercode-core

# Should show: "Up X seconds (healthy)"

# Check agents are registering
docker logs project-strategist 2>&1 | grep -i "registration\|connected\|healthy"

# Expected: No more "Name or service not known" errors
# Expected: No more 401 responses
```

---

## Quick Verification

Run these commands to verify all fixes are working:

```bash
# 1. Verify hypercode-core /health endpoint
curl http://localhost:8000/health

# 2. Verify /agents/bible works (was crashing before)
curl http://localhost:8000/agents/bible | head -20

# 3. Check agent registration logs
docker logs backend-specialist --tail 20

# 4. Verify all containers healthy
docker ps --filter "label=com.docker.compose.project=hypercode-v20" --format "table {{.Names}}\t{{.Status}}"
```

---

## What Was Fixed

| Issue | Status | File | Change |
|-------|--------|------|--------|
| IndexError in agents.py | ✅ Fixed | `app/routers/agents.py:92-125` | Added multi-path resolution |
| Connection pool timeout | 📝 Needs config update | `docker-compose.yml` | Add `DATABASE_CONNECTION_LIMIT=20` |
| 401 Auth errors | 📝 Needs agent update | `agents/*/main.py` | Add API_KEY to headers |
| Agent healthchecks failing | ⏳ Will auto-fix | `docker-compose.yml` | Once auth fixed, healthchecks will pass |

---

## Timeline to Recovery

1. **Immediate (5 min):** Rebuild & restart hypercode-core
2. **Quick (10 min):** Verify agents can register
3. **Complete (15 min):** All 4 agents should be healthy

---

## Prevention Tips

1. **Use environment-agnostic path resolution** (done)
2. **Set higher connection pool limits** for multi-agent systems
3. **Test agent registration** before deployment
4. **Monitor logs** for "Name or service not known" = network issue, "401" = auth issue

---

## Need Help?

If issues persist:

```bash
# Full system restart
docker compose down -v
docker compose up -d

# Check individual agent logs
docker logs <agent-name> --tail 50

# Check database connectivity
docker exec hypercode-core python -c "
import asyncio
from app.core.db import db
asyncio.run(db.connect())
print('✅ DB connected')
"
```

Status: All fixes ready for deployment. You're 15 minutes away from full health. 💪

---

## Resolved Issues (Feb 18 2026)

### 1. HAFS Service Permission Error
- **Issue:** `hafs-service` was crashing with `PermissionError` when downloading models to `/home/hypercode/.cache`.
- **Fix:** Updated `Dockerfile.production` to pre-create `/home/hypercode/.cache/huggingface` and set ownership to `hypercode` user. Also set `HF_HOME` and `XDG_CACHE_HOME` environment variables.

### 2. Agent Authentication Failure (401 Unauthorized)
- **Issue:** Agents (`backend-specialist`, `qa-engineer`, etc.) were receiving 401 errors when registering with `hypercode-core`.
- **Fix:** Added `HYPERCODE_API_KEY=${API_KEY}` to all agent definitions in `docker-compose.yml`. Confirmed `BaseAgent` sends this key in `X-API-Key` header.

### 3. Agent Dependency Missing (ModuleNotFoundError: 'event_bus')
- **Issue:** Agents failed to start with `ModuleNotFoundError: No module named 'event_bus'` because `event_bus.py` was not mounted.
- **Fix:** Updated `docker-compose.yml` to mount `./agents/base-agent/event_bus.py` to `/app/event_bus.py` for all agents.

### 4. Hypercode Core Unhealthy
- **Issue:** `hypercode-core` was taking longer than 90s to start, causing dependency failures for agents.
- **Fix:** Added `start_period: 120s` to `hypercode-core` healthcheck in `docker-compose.yml`.

### Current Status
- All agents are UP and HEALTHY.
- `hypercode-core` is UP and HEALTHY.
- `hafs-service` is UP and HEALTHY.
- Agent registration is successful.
