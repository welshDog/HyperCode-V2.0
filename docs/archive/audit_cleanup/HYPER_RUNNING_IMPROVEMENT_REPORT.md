# Hyper Running Mode: Improvement Report & Roadmap

## 1. Executive Summary
The concept of **Hyper Running Mode**—a self-improving agent swarm visualized in real-time—is highly aligned with the HyperCode vision. The provided specifications (`BROski Terminal Hyper Swarm` and `hyper-running.md`) offer a solid foundation. However, the proposed MVP architecture (JSONL files, in-memory state) introduces unnecessary latency and fragility given the existing infrastructure (Redis, FastAPI).

This report proposes shifting the "Transport" layer to **Redis + Server-Sent Events (SSE)** immediately to ensure a true "live" experience and robustness, along with specific safety and workflow enhancements.

## 2. Gap Analysis & Critiques

| Area | Current Proposal | Issue / Gap | Recommendation |
| :--- | :--- | :--- | :--- |
| **Transport** | JSONL File Tailing | High latency; file locking issues; requires complex file reading API. | **Redis Pub/Sub + SSE**. Core already has `redis` and `sse-starlette`. Push events instantly to frontend. |
| **State** | Orchestrator In-Memory | State lost on restart; not scalable; hard to query from external tools. | **Redis Hash**. Store agent status in `agent:status:{id}`. Single source of truth. |
| **Safety** | "Non-destructive improvements" | Vague definition; relies on agent discretion. | **Strict Scopes**. MVP Sprints restricted to `docs/`, `tests/`, or specific file patterns. |
| **Workflow** | Fully Autonomous | High risk of runaway loops or bad edits in early versions. | **Human-in-the-Loop Gate**. Strategist proposes Plan → User Approves → Swarm Executes. |
| **HAFS** | "Scans repo" | Unclear mechanism for "scanning". | **Vector Search + Tree Walk**. Explicitly define how Strategist identifies "bad code" (e.g., `grep "TODO"`, low coverage metrics). |

## 3. Concrete Recommendations

### A. Architecture Upgrade: "Live Nerve System"
Instead of writing to files, we utilize the existing Redis infrastructure.

1.  **Agents** publish events to Redis Channel: `hypercode.events`.
2.  **HyperCode Core** subscribes to this channel.
3.  **API Endpoint** `GET /events/stream` (SSE) forwards these events directly to BROski Terminal.
4.  **Orchestrator** persists `agent:status` in Redis for state recovery.

### B. Workflow Refinement: The "Approval" Step
To ensure safety and build trust:
1.  **Kickoff**: User clicks "Start Hyper Run".
2.  **Analysis**: Strategist scans and generates `proposed_sprint.json` (3 tasks).
3.  **Review**: BROski Terminal displays the plan.
4.  **Approval**: User clicks "Execute".
5.  **Execution**: Swarm activates.

### C. Error Handling Strategy
-   **Timeout Watchdog**: If an agent stays in `status: working` for > 5 minutes without a heartbeat, mark as `stalled` and emit alert.
-   **Rollback Capability**: Agents should commit to a `hyper-run/task-id` branch. If verification fails, the branch is discarded (Git integration required).

## 4. Revised Implementation Plan (Phased)

### Phase 1: The Nervous System (Core & Base Agent)
-   [ ] Implement `EventBus` in `hypercode-core` wrapping Redis Pub/Sub.
-   [ ] Update `BaseAgent` with `self.emit_event(type, payload)` method.
-   [ ] Create `GET /events/stream` SSE endpoint in Core.

### Phase 2: Visibility (Frontend)
-   [ ] Build **Swarm Board**: Grid of agents listening to the SSE stream.
-   [ ] Build **Live Feed**: Scrolling terminal log of all events.

### Phase 3: The Brain (Strategist & Orchestrator)
-   [ ] Implement `Strategist.analyze_codebase()` skill (find TODOs, lint errors).
-   [ ] Create `POST /hyper-running/plan` (Returns plan).
-   [ ] Create `POST /hyper-running/execute` (Accepts plan_id).

## 5. Success Criteria Checklist

- [ ] **Real-Time**: Events appear in BROski Terminal < 200ms after agent emission.
- [ ] **Persistence**: Agent status survives a `docker-compose restart`.
- [ ] **Safety**: Agents cannot modify files outside the agreed "Sprint Scope" (enforced via file system permissions or pre-commit hooks).
- [ ] **Observability**: Every agent action (HAFS query, File Write, Shell Command) emits a distinct event.
- [ ] **Recovery**: If the Orchestrator dies, the Sprint state is recoverable from Redis.

## 6. Next Immediate Step
**Authorize the upgrade of `BaseAgent` and `HyperCode Core` to support Redis-based Event Emission.** This is the prerequisite for all visual features.
