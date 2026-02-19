You gave me two killer options; I have to pick one. Given where HyperCode is heading, the **ILA‑Agent mode spec** will give you more immediate build value and is easier to plug into your repo, so I’ll do that. If you want the “Every Brain is an Esolang” essay next, we can knock that out as a follow‑up.  

Below is a **ready‑to‑commit** Markdown spec you can drop into `docs/specs/ila-agent-mode.md` (or similar). You can tweak naming but the structure is production‑grade.  

***

# ILA‑Agent Mode – HyperCode IDE Technical Specification

**Status:** Draft  
**Owner:** HyperCode Core Team  
**Last updated:** 2026‑02‑17  

## 1. Overview

ILA‑Agent mode (“Inference‑time Language Acquisition Agent mode”) extends HyperCode IDE with an AI‑native workflow where agents can **learn, adapt to, and assist with unfamiliar or user‑defined language dialects** at inference time, inspired by ILA‑style frameworks and esolang benchmarks.  

Core goals:  

- Let users create or enable new *dialects* (syntactic/semantic modules) and have agents learn them interactively.  
- Provide a **multi‑panel IDE experience** where agents explore, run probes, and present distilled knowledge back to the user.  
- Maintain **persistent agent memory** across sessions for dialects, projects, and user preferences.  

***

## 2. Panel Layout Configurations

ILA‑Agent mode defines a default layout and a compact variant. Users can customize, but these are the baselines.

### 2.1 Default Layout (Desktop)

```text
+--------------------------------------------------------------------------------+
| [A] Code Editor (Primary)               | [B] Agent Workspace (Right Panel)    |
|                                         |--------------------------------------|
|   HyperCode source / dialect files      | B1. Conversation & Commands          |
|                                         | B2. Agent Plan & Status              |
+-----------------------------------------+--------------------------------------+
| [C] Context Viewers (Bottom)           | [D] Execution / Logs (Bottom-Right) |
|----------------------------------------|--------------------------------------|
| C1. Dialect Spec  | C2. Knowledge Map  | D1. REPL / Sandbox | D2. Logs       |
+--------------------------------------------------------------------------------+
```

#### Panels

- **[A] Code Editor**  
  - Standard HyperCode editor (text + visual modes).  
  - Inline agent hints (ghost text, annotations, gutter icons).  

- **[B] Agent Workspace**  
  - **B1. Conversation & Commands**  
    - Chat‑style UI (user ↔ agents, agent ↔ agent traces).  
    - Slash‑commands: `/learn-dialect`, `/probe`, `/summarise`, `/explain-snippet`.  
  - **B2. Agent Plan & Status**  
    - Visual list of active tasks: “Read spec”, “Generate probes”, “Run tests”, “Build cheatsheet”.  
    - Each task shows agent, status (queued/running/done), ETA, and errors.  

- **[C] Context Viewers**  
  - **C1. Dialect Spec Viewer**  
    - Renders the current dialect definition from the HyperDialect registry (YAML/JSON + docs).  
  - **C2. Knowledge Map**  
    - Visual graph of learned constructs (nodes: “loop”, “pipe”, “2D grid move”; edges: “uses”, “expands to”).  
    - Click to jump to examples and explanations.  

- **[D] Execution / Logs**  
  - **D1. REPL / Sandbox**  
    - Executes snippets in the selected dialect or core HyperCode.  
    - Used by agents for probes and by users for experimentation.  
  - **D2. Logs & Traces**  
    - Timeline of probes, errors, and agent actions.  
    - Filter per agent or per dialect.  

### 2.2 Compact Layout (Laptop / Low‑Distraction)

```text
+----------------------------------------------------------+
| [A] Code Editor                                          |
+-----------------------------+----------------------------+
| [B] Agent Workspace (Tabs) | [C/D] Context/Exec (Tabs)  |
+-----------------------------+----------------------------+
```

- Agent Workspace and Context/Exec are shown as tabbed panes with keyboard shortcuts to flip quickly (for ADHD‑friendly minimal context switching).  

***

## 3. Agent Roles & Interaction Protocol

Three top‑level agent roles: **Intelligence**, **Learning**, **Assistance**. Each role can be implemented by one or more underlying “workers” (LLM backends, tools).

### 3.1 Intelligence Agent

**Purpose:** High‑level planner and orchestrator.  

**Responsibilities:**

- Decide which tools (compiler, interpreter, test runner) and which sub‑agents to invoke.  
- Maintain a **task graph** for language learning and assistance.  
- Resolve conflicts between agents (e.g., contradicting explanations).  

**Capabilities:**

- Access to project metadata, dialect registry, and user preferences.  
- Can spawn subtasks, assign them to Learning/Assistance agents, and merge results.  

**Interaction Protocol:**

- Receives *intent messages* from UI (user actions) and other agents.  
- Emits *plan messages* and *task assignments* to Learning/Assistance agents.  

### 3.2 Learning Agent

**Purpose:** Implement the core ILA loop – reading docs, running probes, building a mental model of the dialect.  

**Responsibilities:**

- Parse dialect specs (YAML/JSON + docs) into internal representations.  
- Design and execute **probe programs** via the sandbox.  
- Infer syntax, semantics, and idioms from execution feedback.  
- Build and update the Dialect Knowledge Base (DKB).  

**Capabilities:**

- Run code in sandbox with different inputs.  
- Request “what‑if” runs (“execute with altered environment”).  
- Tag constructs with confidence scores and known limitations.  

**Interaction Protocol:**

- Accepts *LearnDialect*, *ProbeDialect*, *ValidateHypothesis* tasks from Intelligence.  
- Produces *DialectFacts*, *Examples*, *Cheatsheets*, *FailureCases*.  

### 3.3 Assistance Agent

**Purpose:** User‑facing guidance; uses the DKB to assist coding in the dialect.  

**Responsibilities:**

- Offer code completion, explanation, and translation between dialects.  
- Suggest refactors and guardrails (e.g., “this construct isn’t supported in dialect X”).  
- Generate docs and examples from the DKB.  

**Capabilities:**

- Access to current editor buffer, user selection, and DKB.  
- Inline annotations and quick‑fix suggestions.  

**Interaction Protocol:**

- Receives *AssistUser* and *Explain* intents from UI and Intelligence.  
- Queries DKB and returns inline hints, doc cards, and code snippets.  

***

## 4. Data Flow Diagrams

### 4.1 High‑Level Learning Flow (UML Activity)

```text
User -> UI: /learn-dialect my-dialect
UI -> IntelligenceAgent: Intent(LearnDialect, dialectId)

IntelligenceAgent -> DialectRegistry: FetchSpec(dialectId)
DialectRegistry -> IntelligenceAgent: DialectSpec

IntelligenceAgent -> LearningAgent: Task(LearnDialect, DialectSpec)

LearningAgent -> Sandbox: RunProbes(ProbeSet)
Sandbox -> LearningAgent: ProbeResults

LearningAgent -> DKB: Update(Facts, Examples, Confidence)

LearningAgent -> IntelligenceAgent: TaskResult(Summary, Coverage)

IntelligenceAgent -> AssistanceAgent: NotifyDialectReady(dialectId)

AssistanceAgent -> UI: ShowCheatsheet(dialectId), EnableHints(dialectId)
```

### 4.2 Assistance Flow (Sequence Diagram)

```text
User -> UI: Requests explanation for selected code
UI -> AssistanceAgent: AssistUser(ExplainSnippet, code, dialectId, context)

AssistanceAgent -> DKB: QueryFacts(code, dialectId)
DKB -> AssistanceAgent: Facts, Examples

AssistanceAgent -> UI: InlineExplanation + OptionalRefactor
```

### 4.3 Agent‑to‑Agent Collaboration

```text
IntelligenceAgent -> LearningAgent: "Hypothesis #7 conflicts with compiler error logs"
LearningAgent -> Sandbox: "Rerun probe with modified syntax"
Sandbox -> LearningAgent: "New error pattern"
LearningAgent -> DKB: "Update hypothesis, lower confidence, mark 'unstable'"
LearningAgent -> AssistanceAgent: "Avoid suggesting construct X in dialectId"
AssistanceAgent -> UI: "Deprecation/Warning banner in hints"
```

***

## 5. API Endpoints & Message Formats

Assume HyperCode runs an internal **Agent Bus** (e.g., WebSocket or message queue) with a JSON‑based protocol.

### 5.1 Common Envelope

```jsonc
{
  "id": "uuid-4",
  "type": "Intent|Task|Result|Event",
  "sender": "UI|IntelligenceAgent|LearningAgent|AssistanceAgent|Service",
  "recipient": "IntelligenceAgent|LearningAgent|AssistanceAgent|Service|Broadcast",
  "timestamp": "2026-02-17T12:00:00Z",
  "payload": { /* type-specific */ }
}
```

### 5.2 Intents from UI

#### Learn Dialect

```jsonc
{
  "type": "Intent",
  "sender": "UI",
  "recipient": "IntelligenceAgent",
  "payload": {
    "kind": "LearnDialect",
    "dialectId": "hypercode.esolang.befunge2d",
    "projectId": "project-123",
    "options": {
      "maxProbeBudget": 50,
      "aggressiveness": "balanced"
    }
  }
}
```

#### Explain Snippet

```jsonc
{
  "type": "Intent",
  "sender": "UI",
  "recipient": "AssistanceAgent",
  "payload": {
    "kind": "AssistUser",
    "mode": "ExplainSnippet",
    "dialectId": "hypercode.esolang.befunge2d",
    "code": ">>v\n^ <",
    "editorContext": {
      "filePath": "src/main.hc",
      "selectionRange": [10, 24]
    }
  }
}
```

### 5.3 Tasks from Intelligence to Learning

```jsonc
{
  "type": "Task",
  "sender": "IntelligenceAgent",
  "recipient": "LearningAgent",
  "payload": {
    "kind": "LearnDialect",
    "dialectId": "hypercode.esolang.befunge2d",
    "dialectSpec": { /* inlined spec or reference */ },
    "probeConfig": {
      "strategies": ["random-small", "pattern-based", "boundary-tests"],
      "maxProbes": 50
    }
  }
}
```

### 5.4 Sandbox API

HTTP or IPC API from agents to execution engine:

```http
POST /sandbox/run
Content-Type: application/json
```

```jsonc
{
  "dialectId": "hypercode.esolang.befunge2d",
  "source": ">>v\n^ <",
  "inputs": ["input1", "input2"],
  "timeoutMs": 2000
}
```

Response:

```jsonc
{
  "status": "ok|compile_error|runtime_error|timeout",
  "stdout": ["..."],
  "stderr": ["..."],
  "meta": {
    "cpuMs": 12,
    "memoryBytes": 20480,
    "exitCode": 0
  }
}
```

***

## 6. State Management Requirements

### 6.1 Dialect Knowledge Base (DKB)

Persistent store (e.g., SQLite/Postgres table or document DB) keyed by `dialectId` + `projectId`.

Schema sketch:

```sql
CREATE TABLE dialect_knowledge (
  id TEXT PRIMARY KEY,
  dialect_id TEXT NOT NULL,
  project_id TEXT,
  kind TEXT NOT NULL,            -- "construct", "pattern", "restriction", ...
  key TEXT NOT NULL,             -- e.g. "loop", "pipe-forward"
  description TEXT,
  example_code TEXT,
  example_output TEXT,
  confidence REAL,               -- 0.0 .. 1.0
  metadata JSONB,                -- arbitrary (source, probeIds, etc.)
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### 6.2 Agent State

- Each agent instance maintains an in‑memory state:  
  - Current task queue, last N messages, probe history cache.  
- Periodically serialized to disk for **session resume**.  

Serialized format (per agent + project):

```jsonc
{
  "agentId": "learning-agent",
  "projectId": "project-123",
  "dialectId": "hypercode.esolang.befunge2d",
  "taskQueue": [ /* pending tasks */ ],
  "recentMessages": [ /* last 100 message envelopes */ ],
  "probeHistory": [ /* compressed records */ ]
}
```

### 6.3 Context Lifetimes

- **Project context:** long‑lived, includes DKB and agent learned preferences.  
- **Session context:** UI session; caches in‑memory state, cleared when IDE is closed.  
- **Ephemeral context:** single operation (e.g., one `/probe` run).  

***

## 7. Integration Points with Existing HyperCode Modules

Assuming current modules:

- `core/compiler` – HyperCode compiler / transpiler.  
- `core/interpreter` – runtime + sandbox.  
- `core/dialects` – registry of dialect metadata and loaders.  
- `ui/editor` – code editor.  
- `ui/panels` – panel management.  
- `runtime/agents` – existing agent orchestration (if any).  

### 7.1 Dialect Registry

Add support for **ILA metadata**:

```yaml
id: hypercode.esolang.befunge2d
name: "Befunge2D Dialect"
baseLanguage: "hypercode-core"
ila:
  probeStrategies:
    - random-small
    - directional-grid
  maxDefaultProbeBudget: 100
  hints:
    recommendedAgents: ["learning-agent-v1"]
```

### 7.2 Sandbox Integration

- Expose `/sandbox/run` endpoint to agents (see §5.4).  
- Provide “safe mode” for untrusted esolangs (CPU/memory/time limits).  

### 7.3 UI Integration

- Add “ILA‑Agent mode” toggle in the IDE.  
- Add commands:  
  - `HyperCode: Learn Current Dialect`  
  - `HyperCode: Show Dialect Knowledge Map`  
  - `HyperCode: Explain Selection (ILA)`  

***

## 8. Performance & Scalability Considerations

### 8.1 Probe Budget & Scheduling

- **Hard cap** on concurrent probe runs per project (configurable, default 8).  
- Rate limit per agent: N probe requests / minute per dialiect.  
- Cancellation: user can cancel learning sessions; agents must gracefully stop, log partial knowledge.  

### 8.2 Caching

- Cache probe results keyed by `(dialectId, sourceHash, inputsHash)` to avoid duplicate execution.  
- Cache DKB query results for common queries (like “explain this construct”).  

### 8.3 Latency Targets

- Inline assistance (completion / quick explain): P95 < 500 ms (excluding LLM latency).  
- Probe‑driven learning sessions: P95 per probe < 2 s; user sees incremental updates rather than one huge batch.  

### 8.4 Horizontal Scaling

- Agents should be stateless workers using DKB and Agent State store.  
- Agent Bus can route tasks to multiple Learning/Assistance workers.  

***

## 9. Security Protocols for Agent Operations

### 9.1 Sandbox Isolation

- All agent‑initiated code execution runs in an isolated sandbox:  
  - No network access by default.  
  - Limited filesystem access (project dir only, read‑only by default).  
  - Resource limits (CPU, memory, time).  

### 9.2 Permission Model

- Agents cannot:  
  - Commit code changes without explicit user approval.  
  - Access secrets (API keys, wallet keys) unless user opts in and scopes access.  

- Permission prompts:  
  - “Allow Learning Agent to read `docs/dialect.md`?”  
  - “Allow Assistance Agent to apply refactor to 3 files?”  

### 9.3 Logging & Audit

- All agent actions are logged to D2 Logs & Traces with:  
  - Agent ID, operation type, affected files/resources, timestamps.  
- Audit trail can be exported as JSON for debugging / compliance.  

***

## 10. Testing Framework Requirements

### 10.1 Unit Tests

- Agent message handlers (serialization/deserialization).  
- DKB read/write operations (including migrations).  
- Sandbox API client (error handling, retries, timeouts).  

Example (pseudo‑TypeScript):

```ts
test("LearningAgent persists dialect facts", async () => {
  const agent = new LearningAgent(fakeDKB, fakeSandbox);
  await agent.handleTask({
    kind: "LearnDialect",
    dialectId: "hypercode.esolang.toy",
    dialectSpec: mockSpec
  });

  const facts = await fakeDKB.listFacts("hypercode.esolang.toy");
  expect(facts.length).toBeGreaterThan(0);
  expect(facts[0].confidence).toBeGreaterThan(0.5);
});
```

### 10.2 Integration Tests

- End‑to‑end: `/learn-dialect` → probes → DKB → assistance hints in editor.  
- Error paths:  
  - Sandbox failures (crash, timeout).  
  - Partial spec (missing sections).  
  - Conflicting facts.  

### 10.3 Performance Tests

- Stress tests with many concurrent probe tasks.  
- Benchmark DKB queries with large fact sets (~100k entries) for complex dialects.  

### 10.4 UX/ND‑focused Tests

- Ensure layout scales for low‑vision/high‑contrast themes.  
- Keyboard‑only flow for `/learn-dialect` and explanation.  
- Minimal context switch: check that essential commands are reachable via single keystrokes.  

***

## 11. Deployment Configuration Templates

### 11.1 Local Dev (Single‑User)

```yaml
ilaAgentMode:
  enabled: true
  bus:
    type: inprocess
  sandbox:
    maxConcurrent: 4
    timeoutMs: 2000
  dkb:
    driver: sqlite
    file: ".hypercode/dkb.db"
  agents:
    intelligence:
      implementation: "local-llm"  # configurable backend
    learning:
      implementation: "local-llm"
    assistance:
      implementation: "local-llm"
```

### 11.2 Team / Cloud Deployment

```yaml
ilaAgentMode:
  enabled: true
  bus:
    type: nats
    url: "nats://ila-bus.internal:4222"
  sandbox:
    maxConcurrent: 64
    timeoutMs: 5000
    poolSize: 16
  dkb:
    driver: postgres
    uri: "postgres://hypercode:***@db:5432/hypercode"
  agents:
    intelligence:
      implementation: "openai-gpt"
      apiKeyEnv: "HYPERCODE_OPENAI_KEY"
    learning:
      implementation: "openai-gpt"
      apiKeyEnv: "HYPERCODE_OPENAI_KEY"
    assistance:
      implementation: "openai-gpt"
      apiKeyEnv: "HYPERCODE_OPENAI_KEY"
  security:
    sandboxNetworkAccess: false
    allowAgentFileWrites: false
```

### 11.3 Docs Placement

- Place this spec at:  
  - `docs/specs/ila-agent-mode.md`  
- Cross‑link from:  
  - `docs/architecture/agents.md`  
  - `docs/user/ila-mode-guide.md` (later).  
