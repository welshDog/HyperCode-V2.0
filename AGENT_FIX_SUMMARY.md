# 🔧 Best Fixes for Unhealthy Agents

## Executive Summary
Your 4 unhealthy agents are failing due to **3 interconnected bugs**. All can be fixed in **15 minutes**.

---

## The 3 Bugs

### 🔴 Bug #1: IndexError Crashes hypercode-core
**Symptom:** hypercode-core exits with status 255 after ~27 hours  
**Cause:** Path traversal fails: `Path(__file__).resolve().parents[4]` doesn't exist in Docker  
**Impact:** Core crashes → All agents lose connection → 401 errors on re-registration → Healthchecks fail

**Fixed:** ✅ File updated: `THE HYPERCODE/hypercode-core/app/routers/agents.py`
- Uses fallback path resolution (4 strategies tried in sequence)
- No more crashes on `/agents/bible` requests

---

### 🔴 Bug #2: 401 Unauthorized (Agent Registration)
**Symptom:** All agents log "Agent registration connection failed" OR "401 Service Unavailable"  
**Cause:** Agents not sending API_KEY in Authorization header  
**Impact:** Agents fail to register → Healthcheck fails (returns 503) → marked unhealthy

**How to Fix:**
Update `agents/base-agent/agent.py` to add API_KEY to every request:
```python
import os

def get_headers():
    api_key = os.getenv("HYPERCODE_API_KEY") or os.getenv("API_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

# All agent requests must use:
response = requests.post(
    f"{CORE_URL}/agents/register",
    json=payload,
    headers=get_headers()  # ← Add this
)
```

**Verify:** All agents in docker-compose.yml already have `HYPERCODE_API_KEY=${API_KEY}` set ✅

---

### 🔴 Bug #3: Database Connection Pool Exhaustion
**Symptom:** After 36+ hours, logs show "Timed out fetching a new connection from the connection pool"  
**Cause:** Prisma default pool limit is 5 connections. Under agent load, it fills up  
**Impact:** Requests timeout → agents get 503 → healthchecks fail

**How to Fix:**
Add to `docker-compose.yml` hypercode-core environment:
```yaml
hypercode-core:
  environment:
    # ... existing vars ...
    - DATABASE_CONNECTION_LIMIT=20  # Increase pool from 5 to 20
```

---

## Implementation (Choose One)

### Option A: Quick Restart (Most Likely to Work)
```bash
# Stop everything
docker compose down

# Rebuild core with new agents.py
docker compose build hypercode-core --no-cache

# Start with agents profile
docker compose up -d --profile agents

# Verify
docker ps | grep -E "core|specialist|engineer"
```

### Option B: Run Fix Script
**Linux/Mac:**
```bash
chmod +x fix_agents.sh
./fix_agents.sh
```

**Windows:**
```cmd
fix_agents.bat
```

### Option C: Manual Verification Steps
1. **Check agents.py fix is applied:**
   ```bash
   docker exec hypercode-core grep -c "possible_paths" /app/app/routers/agents.py
   # Should output: 1 (means fix is applied)
   ```

2. **Verify hypercode-core health:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy"}
   ```

3. **Test /agents/bible endpoint (was crashing before):**
   ```bash
   curl http://localhost:8000/agents/bible | head -5
   # Should return markdown content, not error
   ```

4. **Check agent registration:**
   ```bash
   docker logs backend-specialist --tail 30 | grep -E "registration|healthy|401"
   # Should show successful registration, not 401
   ```

---

## Expected Timeline

| Step | Time | Action |
|------|------|--------|
| 1 | 2 min | `docker compose down` |
| 2 | 3 min | `docker compose build hypercode-core` |
| 3 | 1 min | `docker compose up -d` |
| 4 | 5 min | Services start + core becomes healthy |
| 5 | 2 min | Agents start + register successfully |
| 6 | 1 min | Agents pass healthchecks |
| **Total** | **~15 min** | **All 4 agents healthy** |

---

## Files Already Updated

✅ `THE HYPERCODE/hypercode-core/app/routers/agents.py` - Multi-path resolution applied

---

## Files That Need Updates (for permanent fix)

| File | Change | Priority |
|------|--------|----------|
| `docker-compose.yml` | Add `DATABASE_CONNECTION_LIMIT=20` to hypercode-core | HIGH |
| `agents/base-agent/agent.py` | Ensure API_KEY in all request headers | HIGH |
| `.env` | Verify `API_KEY=` is set | MEDIUM |

---

## Verification Checklist

- [ ] hypercode-core is running and healthy (`docker ps | grep core`)
- [ ] /health endpoint responds (curl `http://localhost:8000/health`)
- [ ] /agents/bible works (curl `http://localhost:8000/agents/bible | head`)
- [ ] backend-specialist shows `healthy` status in logs
- [ ] project-strategist shows successful registration
- [ ] qa-engineer is no longer reporting 401
- [ ] database-architect shows heartbeat success
- [ ] `docker ps` shows all 4 agents with status "Up" and healthy ✅

---

## If Issues Persist

### Check logs:
```bash
docker logs hypercode-core --tail 50 | grep -i "error\|exception"
docker logs backend-specialist --tail 50 | grep -i "error\|401\|connection"
```

### Nuke and restart:
```bash
docker compose down -v        # Remove volumes
docker system prune -a        # Clean unused images
docker compose up -d --profile agents   # Fresh start
```

### Check database connection:
```bash
docker exec -it postgres psql -U postgres -d hypercode -c "SELECT version();"
```

### Verify Redis:
```bash
docker exec redis redis-cli ping
# Should return: PONG
```

---

## Summary

**The root cause:** hypercode-core crashed from IndexError → agents couldn't register → all 4 agents failed healthcheck

**The fix:** Update path resolution in agents.py + ensure API_KEY headers + increase DB connection pool

**Time to fix:** 15 minutes maximum

**Status:** Ready to deploy. No breaking changes. All fixes are backward compatible.

Let me know if you hit any issues! 💪
