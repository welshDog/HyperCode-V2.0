# Hyper Running Mode – Agent Swarm Spec

## Purpose
Create a **Hyper Running Mode** where all agents work together to **improve HyperCode itself**, and the whole process is **visible in BROski Terminal**.

This document is for AI agents (Agent X, Orchestrator, Strategist, Specialists) to implement and extend.

---

## High-Level Vision

Hyper Running Mode = a live command center where:

- The **Orchestrator** coordinates improvement tasks.
- **Specialist agents** (Backend, QA, DB, DevOps, etc.) work on those tasks.
- **HAFS** provides context, code locations, and related history.
- **BROski Terminal** shows a **live visualization** of the swarm working.

Core ideas:

1. Agents don’t just work on user stories – they work on **improving HyperCode itself**.
2. The system emits **structured events** for every key action.
3. BROski Terminal consumes those events and renders a **Swarm View**.

---

## Phase 1 – Event System (Backend)

### Goal
Add a minimal, generic **event emission** system so that orchestrator + agents can report what they are doing.

### Event Shape

Emit JSON events like this:

```json
{
  "timestamp": "2026-02-18T15:40:00Z",
  "type": "task_assigned",
  "agent": "backend-specialist",
  "task_id": "T-00123",
  "summary": "Refactor authentication middleware for clarity and logging",
  "details": {
    "priority": "high",
    "source": "hyper-running",
    "files": ["agents/security/auth.py", "agents/security/middleware.py"]
  }
}
```

### Minimum Event Types

Agents/orchestrator should emit at least:

- `task_created`
- `task_assigned`
- `task_started`
- `task_completed`
- `task_failed`
- `hafs_query` (includes query + top files)
- `fix_applied` (includes files modified)
- `tests_run` (includes result summary)

### Transport

MVP options (pick one):

1. **JSONL log file** (simplest)
   - Path: `logs/events.jsonl`
   - Append one JSON object per line.

2. **Redis pub/sub**
   - Channel: `hypercode.events`
   - Publish each event as JSON string.

Start with **JSONL file** for simplest integration, then upgrade later if needed.

### Orchestrator Integration

- When a task is planned → emit `task_created`.
- When a task is delegated → emit `task_assigned`.
- When an agent reports progress → emit `task_started` / `task_completed` / `task_failed`.

### Agent Integration

Each agent should:

- Emit `task_started` when beginning work.
- Emit `hafs_query` when calling HAFS.
- Emit `fix_applied` when changing files.
- Emit `tests_run` when executing tests.
- Emit `task_completed` or `task_failed` at the end.

---

## Phase 2 – Agent Status API (Core)

### Goal
Expose a simple API so BROski Terminal can query **current agent status**.

### Endpoint

`GET /agents/status`

**Response example:**

```json
{
  "timestamp": "2026-02-18T15:45:00Z",
  "agents": [
    {
      "name": "backend-specialist",
      "role": "Backend Specialist",
      "status": "working",   
      "current_task_id": "T-00123",
      "current_task_summary": "Refactor authentication middleware",
      "last_seen": "2026-02-18T15:44:55Z"
    },
    {
      "name": "qa-engineer",
      "role": "QA Engineer",
      "status": "idle",
      "current_task_id": null,
      "current_task_summary": null,
      "last_seen": "2026-02-18T15:44:30Z"
    }
  ]
}
```

Implementation detail:

- Orchestrator keeps a small in-memory/state store of `agent_status` and updates it whenever events occur.
- Core exposes that via HTTP.

---

## Phase 3 – Swarm View in BROski Terminal (Frontend)

### Goal
Create a **Swarm View** panel in BROski Terminal that:

1. Shows each agent as a **card** with status.
2. Renders a **live activity feed** from events.
3. Allows toggling **Hyper Running Mode** on/off.

### UI Sections

1. **Agent Grid (Top)**
   - One card per agent:
     - Name (e.g., `Backend Specialist`)
     - Status pill: `idle`, `working`, `blocked`, `error`.
     - Current task short text.
     - Subtle pulse animation when state changes.

2. **Event Feed (Middle)**
   - Chronological list from the last N events.
   - Color-coded by:
     - Agent
     - Event type (e.g., `task_*`, `fix_applied`, `tests_run`).

3. **Controls (Bottom)**
   - Button: `Start Hyper Running Sprint`
   - Button: `Pause`
   - Dropdown: focus filter (e.g., `Show only Backend + QA`).

### Data Sources

- `GET /agents/status` → Agent cards.
- `GET /events?limit=100` → Event feed (or WebSocket/stream if available).

---

## Phase 4 – Hyper Running Sprint Flow

### Goal
Have agents not just respond to user tasks, but **spawn their own improvement sprints** for HyperCode.

### High-Level Flow

1. **Start Sprint** (triggered from BROski button or API call):
   - Endpoint: `POST /hyper-running/start`
   - Body example:

   ```json
   {
     "max_tasks": 3,
     "focus_area": "auth_stability"
   }
   ```

2. **Strategist Agent**:
   - Uses HAFS + repo analysis to propose 1–3 concrete improvement tasks, e.g.:
     - "Improve logging in auth middleware"
     - "Add tests for failed login attempts"
     - "Document session timeout behavior"
   - Emits `task_created` events.

3. **Orchestrator**:
   - Assigns each task to the best agent.
   - Emits `task_assigned` events.

4. **Specialist Agents**:
   - Work each task using HAFS.
   - Emit `hafs_query`, `fix_applied`, `tests_run`, `task_completed`.

5. **QA + DevOps**:
   - QA runs and reports tests.
   - DevOps ensures services stay healthy.

6. **Completion**:
   - When all tasks complete, emit:

   ```json
   {
     "type": "hyper_running_complete",
     "summary": "3 tasks completed successfully",
     "tasks": ["T-00123", "T-00124", "T-00125"]
   }
   ```

### MVP Constraints

- Start with **one sprint at a time**.
- Limit to **1–3 tasks per sprint**.
- Focus first on **non-destructive improvements**:
  - Docs
  - Logging
  - Tests

---

## Phase 5 – Safety & Observability

### Safety Guards

Agents should:

- Prefer PR-style changes (if using git in-container) rather than direct edits in production branches.
- Avoid mass refactors until smaller sprints are proven stable.
- Always run tests (where available) after code changes.

### Observability

- All key actions must create **events**.
- Failures should:
  - Emit `task_failed` with error details.
  - NOT loop infinitely; cap retries.

---

## Phase 6 – Stretch Goals (Future)

These are **nice-to-haves** once the base system is working:

- **Hyper Running Level meter**
  - Level based on:
    - All services healthy
    - Test coverage thresholds
    - Number of open TODOs
  - Visual meter in BROski Terminal.

- **Per-Agent History View**
  - For each agent, show historical tasks completed.

- **Pattern Learning**
  - Use HAFS + event history to find common failure patterns and propose meta-fixes.

---

## Definition of Done (MVP)

Hyper Running Mode MVP is considered **DONE** when:

1. Orchestrator and agents emit structured events to a shared channel (file or Redis).
2. `GET /agents/status` returns live data about each agent.
3. BROski Terminal has a **Swarm View** showing:
   - Agent cards with status.
   - A scrolling activity feed.
4. There is a `POST /hyper-running/start` endpoint that:
   - Triggers Strategist → creates 1–3 improvement tasks.
   - Orchestrator assigns those tasks.
   - Specialist agents work on them and emit events.
5. You can visually watch, in BROski Terminal, agents:
   - Plan → assign → execute → test → complete **a real internal improvement task** on HyperCode.

When all of the above are true, Hyper Running Mode is **operational**.
