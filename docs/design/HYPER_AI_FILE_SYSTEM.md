# Hyper AI File System Architecture (HAFS)

## 1. Vision & Philosophy
The Hyper AI File System (HAFS) is not just a directory structure; it's a **living, semantic nervous system** for the HyperCode codebase. It transforms a static repository into a dynamic knowledge graph that serves both human developers (neurodivergent-friendly) and AI agents (context-optimized).

### Core Principles
- **Cognitive Ergonomics**: Structure matches mental models, not just compiler requirements.
- **AI-First Navigation**: JSON/Vector indices for O(1) context retrieval by agents.
- **Self-Healing**: The system detects entropy (misplaced files) and suggests or performs reorganization.
- **Predictive Context**: "If you're editing `auth.py`, you probably need `tests/test_auth.py` and `docs/design/security.md`."

---

## 2. System Architecture

### 2.1. The "Neural Layer" (Metadata & Indexing)
Instead of relying on `ls -R`, HAFS maintains a real-time index in `.ai/`:

```json
// .ai/MASTER_INDEX.json (Simplified)
{
  "graph": {
    "nodes": {
      "agents/auth/main.py": { "type": "code", "layer": "backend", "tags": ["security", "critical"] },
      "docs/design/security.md": { "type": "doc", "layer": "design", "tags": ["security"] }
    },
    "edges": [
      { "from": "agents/auth/main.py", "to": "docs/design/security.md", "relation": "implements" }
    ]
  },
  "predictive_patterns": {
    "agents/auth/main.py": ["tests/unit/test_auth.py", "docker-compose.yml"]
  }
}
```

### 2.2. Directory Taxonomy (The "Cortex")
Structure strictly enforces separation of concerns while maintaining "wormholes" (symlinks/references) for ease of access.

- **`root`**: Entry points only (`README`, `docker-compose`, `.env`).
- **`core/`**: The brain (HyperCode Core, Engine).
- **`agents/`**: The workforce (Specialized agents).
- **`docs/`**: The memory (Indexed, graph-linked documentation).
- **`platform/`**: The body (Docker, K8s, Infrastructure).
- **`interface/`**: The face (BROski Terminal, CLI).
- **`.ai/`**: The subconscious (Indices, embeddings, context maps).

### 2.3. Intelligent Components

#### A. The `ContextWalker` Engine
Located at `scripts/hafs/walker.py`, this engine queries the `.ai/MASTER_INDEX.json` to provide:
- **Context Retrieval**: `get_context(path)` returns metadata, imports, and importers.
- **Predictive Suggestions**: `predict_next(path)` uses heuristics (siblings, imports, tests) to suggest relevant files.

#### B. The `HAFS Watcher` (Reactive Indexing)
Located at `scripts/hafs/watcher.py` (entry: `scripts/start_hafs.py`), this service:
- Monitors the file system for changes (creates, modifies, moves).
- Triggers incremental index updates in real-time.
- Ensures the "Neural Layer" is always in sync with the "Physical Layer".

#### C. Semantic Linker
Located at `scripts/hafs/semantic.py`, this module:
- Parses code (Python, TS/JS) to extract import dependencies.
- Maps files to a dependency graph with full import resolution (relative and absolute paths).

#### D. Vector Search Engine (Semantic Deepening)
Located at `scripts/hafs/embeddings.py`, this engine:
- Uses `sentence-transformers/all-MiniLM-L6-v2` to generate embeddings for code files.
- Stores vectors in a local ChromaDB instance (`.ai/chroma_db`).
- Enables semantic search via `python scripts/query_hafs.py "query" --semantic`.

#### F. HAFS API Server (Agent Interface)
Located at `scripts/hafs/server.py`, this FastAPI service provides:
- `/context`: Retrieve file metadata and dependencies.
- `/predict`: Get next-file suggestions.
- `/search`: Semantic search for agents.
- `/diagnose`: Error diagnosis and self-correction.

#### G. Self-Corrector Module
Located at `scripts/hafs/corrector.py`, this agent:
- Analyzes error messages.
- Queries HAFS to find the culprit code.
- Suggests fixes based on semantic context.

#### H. Auto-Documenter
Located at `scripts/hafs/documenter.py`, this pipeline:
- Generates markdown documentation for code files.
- Uses semantic embeddings to link related modules.
- Outputs to `docs/auto_generated/`.

---

## 3. Implementation Status

| Component | Status | Location |
| :--- | :--- | :--- |
| **Taxonomy** | ✅ Done | `docs/`, `agents/`, etc. |
| **Static Index** | ✅ Done | `.ai/MASTER_INDEX.json` |
| **Reactive Watcher** | ✅ Done | `scripts/hafs/watcher.py` |
| **Context Walker** | ✅ Done | `scripts/hafs/walker.py` |
| **Semantic Linking** | ✅ Done | Full import resolution implemented. |
| **Vector Search** | ✅ Done | ChromaDB integration active. |
| **Visualization** | ✅ Done | `docs/design/hafs_graph.html` |
| **Agent API** | ✅ Done | `scripts/hafs/server.py` |
| **Self-Correction** | ✅ Done | `scripts/hafs/corrector.py` |
| **Auto-Docs** | ✅ Done | `scripts/hafs/documenter.py` |

---

## 4. Usage

### Start the Watcher
```bash
python scripts/start_hafs.py
```

### Start the API Server
```bash
python scripts/hafs/server.py
```

### Query Context (Standard)
```bash
python scripts/query_hafs.py agents/crew-orchestrator/main.py
```

### Semantic Search (AI-Powered)
```bash
python scripts/query_hafs.py "authentication logic" --semantic
```

### Visualize the Graph
```bash
python scripts/view_graph.py
```
A background service (Python/Rust) that:
1.  **Watches** file system events (Watchdog).
2.  **Parses** ASTs (Abstract Syntax Trees) to find imports/dependencies.
3.  **Updates** the `MASTER_INDEX.json` and Vector Database (Chroma/FAISS).
4.  **Calculates** "Code Gravity" - pulling related files closer in the index.

#### B. The `EntropyDaemon`
A quality gate that runs on pre-commit or CI:
- Flags files in `root` that belong in subfolders.
- Detects stale documentation (modified code > modified doc).
- Enforces naming conventions (Snake case for Python, Pascal for React).

#### C. The `PredictiveCache`
An API for agents:
- `GET /ai/predict?context=agents/coder/main.py`
- Returns: `["docs/api_reference.md", "tests/test_coder.py"]`
- Reduces agent token usage by pre-fetching relevant context.

---

## 3. Data Structures & Schemas

### 3.1. The HyperGraph Schema
HAFS treats files as nodes in a graph.

```typescript
interface FileNode {
  id: string;          // Relative path
  hash: string;        // Content SHA256
  last_modified: Date;
  semantic_vector: number[]; // Embedding
  meta: {
    language: string;
    imports: string[];
    exported_symbols: string[];
    complexity_score: number;
  };
}

interface Relation {
  source: string;
  target: string;
  type: 'imports' | 'tests' | 'documents' | 'deploys' | 'configures';
  strength: number; // 0-1 confidence
}
```

---

## 4. User Interface Requirements (BROski Terminal)

The "Files" tab in BROski Terminal isn't a tree view; it's a **Context Map**.

1.  **Focus Mode**: Selecting a file centers it, showing linked files orbiting it (Code, Test, Doc, Config).
2.  **Semantic Search**: "Where is the auth logic?" highlights relevant files across folders.
3.  **Entropy Heatmap**: Red zones show messy folders needing reorganization.

---

## 5. Implementation Roadmap

### Phase 1: Structural Hygiene (Immediate)
- [x] Implement `scripts/organize_repo.py` to migrate current chaos to `docs/` categories.
- [ ] Establish `.ai/` directory with static `MASTER_INDEX.json`.

### Phase 2: Reactive Indexing (Next)
- [ ] Create GitHub Action / Git Hook to update index on commit.
- [ ] Implement simple AST parsing to link Code <-> Test.

### Phase 3: The Hyper Brain (Future)
- [ ] Vector embeddings for all docs.
- [ ] Predictive file loading for Agent Context.

---

## 6. Integration with Agents

### Agent Protocol
1.  **Startup**: Agent loads `.ai/PROJECT_CONTEXT.md` (System Prompt).
2.  **Query**: Agent asks `swarmer` or reads `.ai/MASTER_INDEX.json` to find file paths.
3.  **Action**: Agent edits file.
4.  **Feedback**: `ContextWalker` detects change, updates "Last Modified", triggers `EntropyDaemon` check.

This architecture ensures that as the codebase grows (10k+ files), agents remain O(1) efficient in finding context, rather than O(N) drowning in noise.
