# Nexus Integration Documentation

## 1. WebSocket Protocol (BRIDGE)

The BRIDGE agent communicates with the frontend via a robust WebSocket connection.

### Connection
- **URL:** `ws://localhost:8001/ws/bridge`
- **Reconnection:** Exponential backoff (max 30s delay).

### Message Format
All messages are JSON objects.

**Client -> Server:**

1. **Ping:**
   ```json
   {
     "type": "ping"
   }
   ```

2. **Ingest Context:**
   ```json
   {
     "type": "ingest",
     "context_type": "documentation", // or "code", "decision"
     "content": "# Markdown or Code String"
   }
   ```

**Server -> Client:**

1. **Pong:**
   ```json
   {
     "type": "pong"
   }
   ```

2. **Acknowledgment (Ack):**
   ```json
   {
     "type": "ack",
     "request_id": "req_123",
     "status": "success",
     "entry_id": "uuid-entry-id",
     "message": "Optional status message"
   }
   ```

**Broadcast Message:**
```json
{
  "type": "task_update",
  "payload": {
    "status": "success",
    "details": { ... }
  },
  "timestamp": "ISO8601"
}
```

---

## 2. Vector Database (WEAVER)

Weaver uses **ChromaDB** for semantic search and knowledge management.

### Features
- **Semantic Search:** Cosine similarity matching.
- **Batch Ingestion:** `ingest_batch()` with rate limiting.
- **Error Handling:** Robust validation and retry logic.
- **Metadata Tagging:** Auto-extraction of tags from content.

### Configuration
- **Path:** `./data/chroma_db` (Persistent)
- **Collection:** `nexus_knowledge`
- **Distance Metric:** Cosine Similarity

### Schema
| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique entry ID |
| `document` | String | The content (code/doc) |
| `metadata` | JSON | `{"type": "code|doc", "tags": "auth,api"}` |

### Query Pattern
```python
results = weaver.retrieve_context("refactor auth", n_results=5)
```

---

## 3. Perplexity API (CORTEX)

Cortex uses `sonar-pro` for intent understanding.

### Rate Limits
- **Perplexity Pro:** ~1000 requests/day recommended.
- **Handling:** Cortex falls back to mock logic if API fails or key is missing.

### Environment
Ensure `.env` contains:
```bash
PERPLEXITY_API_KEY=pplx-xxxxxxxx
```
