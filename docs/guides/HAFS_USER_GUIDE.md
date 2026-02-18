# Hyper AI File System (HAFS) User Guide

The Hyper AI File System (HAFS) is a cognitive layer that sits on top of the traditional file system. It provides real-time indexing, semantic search, and predictive context for both human developers and AI agents.

## 🚀 Quick Start

### 1. Start the Nervous System
The HAFS Watcher monitors file changes and keeps the AI index up-to-date. Keep this running in a separate terminal.

```bash
python scripts/start_hafs.py
```

### 2. Launch the Agent API
This allows agents (and you) to query the file system intelligence.

```bash
python scripts/hafs/server.py
```
*API will be available at `http://localhost:8001`.*

### 3. Visualize the Codebase
See the neural connections between your files.

```bash
python scripts/view_graph.py
```
*Opens in your browser at `http://localhost:8000`.*

---

## 🔍 Tools & Commands

### Semantic Search
Find code based on what it *does*, not just what it's named.

```bash
# Find authentication logic
python scripts/query_hafs.py "how do we handle jwt tokens?" --semantic

# Find error handling patterns
python scripts/query_hafs.py "error middleware" --semantic
```

### Context Query
Get metadata, dependencies, and predictive suggestions for a file.

```bash
python scripts/query_hafs.py agents/crew-orchestrator/main.py
```

### Auto-Documentation
Generate markdown documentation for any code file.

```bash
python scripts/hafs/documenter.py
# (Edit script to target specific files)
```

---

## 🤖 Agent Integration

Agents can interact with HAFS via the API:

- **`GET /context?path=...`**: Get file context.
- **`GET /predict?path=...`**: Get next-file suggestions.
- **`GET /search?query=...`**: Perform semantic search.
- **`POST /diagnose`**: Submit an error message to find the cause.

### Example: Self-Correction
If an agent encounters an `ImportError`, it can call `/diagnose`:

```json
POST /diagnose
{
  "error_message": "ImportError: cannot import name 'ContextWalker'",
  "file_path": "scripts/main.py"
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "scripts/hafs/walker.py",
      "score": 0.95,
      "snippet": "class ContextWalker: ..."
    }
  ]
}
```
The agent now knows where `ContextWalker` is defined and can fix the import path.

---

## 🏗️ Architecture

- **`scripts/hafs/`**: The core package.
    - `watcher.py`: File system monitor (Watchdog).
    - `indexer.py`: Graph builder.
    - `embeddings.py`: Vector engine (ChromaDB).
    - `walker.py`: Graph traverser.
    - `server.py`: FastAPI interface.
- **`.ai/`**: The brain.
    - `MASTER_INDEX.json`: The knowledge graph.
    - `chroma_db/`: Vector database storage.
