# IDE MCP Servers - Integration Guide

## Overview

Your IDEs (Hyperflow Editor and Broski Terminal) now have MCP servers that allow agents to interact with them programmatically.

---

## Three MCP Servers

### 1. **HyperCode MCP Server** ✅
Agents interact with HyperCode language directly

**Location:** `./agents/mcp-servers/hypercode-mcp-server.py`

**Tools available:**
```
- parse_hypercode()        → Parse HyperCode to AST
- validate_hypercode()     → Check syntax without executing
- execute_hypercode()      → Run code safely
- get_hypercode_examples() → Show language patterns
- format_hypercode_error() → Friendly error messages
- check_hypercode_compatibility()
```

**Use case:** Language Specialist can parse, validate, and understand HyperCode structure

---

### 2. **Hyperflow Editor MCP Server** ✅
Agents interact with the Hyperflow Editor (the IDE you code in)

**Location:** `./agents/mcp-servers/hyperflow-editor-mcp-server.py`

**Tools available:**
```
- check_editor_health()              → Is editor running?
- get_editor_capabilities()          → List all features
- get_syntax_highlighting_config()   → HyperCode syntax colors
- get_autocomplete_suggestions()     → Code completion
- format_error_for_display()         → Format errors for UI
- get_editor_theme()                 → Current theme
- get_keyboard_shortcuts()           → Available shortcuts
- get_file_status()                  → File metadata
- open_file_in_editor()              → Open file programmatically
- get_recent_files()                 → Recently edited files
```

**Use cases:**
- Frontend Specialist can query editor capabilities
- Agents can suggest code completions
- Agents can format errors for display
- Agents can open files in editor for user review

---

### 3. **Broski Terminal MCP Server** ✅
Agents interact with Broski Terminal (the orchestration dashboard)

**Location:** `./agents/mcp-servers/broski-terminal-mcp-server.py`

**Tools available:**
```
- check_terminal_health()     → Is terminal running?
- get_agent_list()            → All registered agents
- get_execution_timeline()    → Event timeline
- filter_timeline_events()    → Filter by agent/type
- search_timeline()           → Find events
- get_agent_metrics()         → Agent performance data
- get_all_metrics()           → System-wide metrics
- export_timeline()           → Export as JSON/CSV
- stream_live_events()        → Live SSE stream URL
- display_metrics_dashboard() → Dashboard URL
- get_context_store()         → Context storage status
```

**Use cases:**
- BROski can check all agents are healthy
- Agents can query execution timeline
- Agents can track their own performance
- Users can export execution history
- Real-time monitoring of tasks

---

## Configuration

Your `agents/mcp-config.json` already has all three servers configured:

```json
{
  "mcpServers": {
    "hypercode": {
      "command": "python",
      "args": ["./agents/mcp-servers/hypercode-mcp-server.py"],
      "env": {
        "HYPERCODE_ENGINE_PATH": "./THE HYPERCODE/hypercode-engine",
        "MCP_LOG_LEVEL": "INFO"
      }
    },
    "hyperflow-editor": {
      "command": "python",
      "args": ["./agents/mcp-servers/hyperflow-editor-mcp-server.py"],
      "env": {
        "EDITOR_PORT": "5173",
        "EDITOR_HOST": "localhost",
        "API_BASE_URL": "http://localhost:8000",
        "MCP_LOG_LEVEL": "INFO"
      }
    },
    "broski-terminal": {
      "command": "python",
      "args": ["./agents/mcp-servers/broski-terminal-mcp-server.py"],
      "env": {
        "TERMINAL_PORT": "3000",
        "TERMINAL_HOST": "localhost",
        "API_BASE_URL": "http://localhost:8000",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## How Agents Use These

### Example 1: Frontend Specialist

```
User: "Add a loading spinner to the run button"

Frontend Specialist:
1. check_editor_health() → Is editor available?
2. get_editor_capabilities() → What can I do?
3. get_syntax_highlighting_config() → How should code look?
4. get_autocomplete_suggestions() → What's available?
5. open_file_in_editor() → Show user the file
```

### Example 2: BROski Orchestrator

```
BROski starts a task:
1. check_terminal_health() → Is dashboard running?
2. get_agent_list() → Who's available?
3. stream_live_events() → Start listening for events
4. [Delegates task to specialists]
5. get_all_metrics() → Get performance summary
6. export_timeline() → Save for user
```

### Example 3: Language Specialist

```
User: "Check if this HyperCode is valid"

Language Specialist:
1. parse_hypercode(source) → Parse to AST
2. validate_hypercode(source) → Check syntax
3. format_hypercode_error() → Make it readable
4. get_hypercode_examples() → Show similar patterns
5. display in editor via hyperflow-editor server
```

---

## Running the Servers

### Start all three:

```bash
# Terminal 1: HyperCode MCP
python ./agents/mcp-servers/hypercode-mcp-server.py

# Terminal 2: Hyperflow Editor MCP
python ./agents/mcp-servers/hyperflow-editor-mcp-server.py

# Terminal 3: Broski Terminal MCP
python ./agents/mcp-servers/broski-terminal-mcp-server.py

# Terminal 4: cagent (will auto-discover the servers)
docker run -v $(pwd):/app \
  -e PERPLEXITY_API_KEY=$PERPLEXITY_API_KEY \
  docker.io/docker/cagent:latest run /app/cagent-pantheon.yaml
```

### Or use docker-compose:

Add to your `docker-compose.yml`:

```yaml
mcp-servers:
  hypercode-mcp:
    build:
      context: .
      dockerfile: Dockerfile.mcp-hypercode
    volumes:
      - ./agents/mcp-servers:/app/mcp-servers
      - ./THE\ HYPERCODE:/app/THE\ HYPERCODE
    environment:
      HYPERCODE_ENGINE_PATH: ./THE HYPERCODE/hypercode-engine
      MCP_LOG_LEVEL: INFO
  
  hyperflow-editor-mcp:
    build:
      context: .
      dockerfile: Dockerfile.mcp-editor
    ports:
      - "5173:5173"  # Editor
    environment:
      EDITOR_PORT: "5173"
      EDITOR_HOST: "localhost"
      API_BASE_URL: "http://localhost:8000"
  
  broski-terminal-mcp:
    build:
      context: .
      dockerfile: Dockerfile.mcp-broski
    ports:
      - "3000:3000"  # Terminal
    environment:
      TERMINAL_PORT: "3000"
      TERMINAL_HOST: "localhost"
      API_BASE_URL: "http://localhost:8000"
```

---

## Environment Variables

| Server | Port | Host | Purpose |
|--------|------|------|---------|
| hypercode-mcp | - | - | Parse/validate HyperCode |
| hyperflow-editor-mcp | 5173 | localhost | IDE capabilities |
| broski-terminal-mcp | 3000 | localhost | Orchestration dashboard |

All three communicate with core API at `http://localhost:8000`

---

## Testing

### Test 1: Check all servers are running

```bash
# In Python
from mcp.client import MCPClient

client = MCPClient()

# Test HyperCode
result = await client.call_tool("hypercode", "parse_hypercode", source='print("hello")')
assert result.success

# Test Hyperflow
result = await client.call_tool("hyperflow-editor", "check_editor_health")
assert result.status in ["healthy", "offline"]

# Test Broski
result = await client.call_tool("broski-terminal", "get_agent_list")
assert len(result.agents) == 7
```

### Test 2: Agent discovers and uses tools

```
Ask BROski:
"List all available agents and their status"

BROski should:
1. Discover broski-terminal MCP server
2. Call get_agent_list()
3. Return list of 7 agents with status
4. Display in Broski Terminal
```

### Test 3: Editor integration

```
Ask Frontend Specialist:
"What keyboard shortcuts are available in the editor?"

Frontend should:
1. Discover hyperflow-editor MCP server
2. Call get_keyboard_shortcuts()
3. Return shortcut list
4. Display nicely formatted
```

---

## Troubleshooting

### Server doesn't start

```bash
# Check Python path
which python
python --version

# Check MCP SDK installed
pip install mcp

# Check ports are available
lsof -i :5173  # Editor
lsof -i :3000  # Terminal

# Try running directly
python ./agents/mcp-servers/hypercode-mcp-server.py
```

### Agent can't find MCP server

```bash
# Make sure mcp-config.json has correct paths
cat ./agents/mcp-config.json

# Check environment variables are set
echo $HYPERCODE_ENGINE_PATH
echo $API_BASE_URL

# Try registering manually
docker run -v $(pwd):/app \
  -e MCP_SERVERS=/app/agents/mcp-config.json \
  docker.io/docker/cagent:latest run /app/cagent-pantheon.yaml
```

### "Connection refused" errors

```bash
# Make sure all services are running
docker compose ps

# Check core API is accessible
curl http://localhost:8000/health

# Check editor is running
curl http://localhost:5173/health

# Check terminal is running
curl http://localhost:3000/api/health
```

---

## What's Next

1. ✅ MCP servers created
2. ✅ Configured in mcp-config.json
3. ✅ Agents can auto-discover them
4. **Next:** Test with cagent orchestrator

```bash
docker run -v $(pwd):/app \
  -e PERPLEXITY_API_KEY=$PERPLEXITY_API_KEY \
  docker.io/docker/cagent:latest run /app/cagent-pantheon.yaml
```

Then ask BROski:
```
"List all agents and show me the editor's keyboard shortcuts"
```

BROski should use BOTH MCP servers and return rich info! 🚀

---

**Files created:**
- `./agents/mcp-servers/hypercode-mcp-server.py` (HyperCode)
- `./agents/mcp-servers/hyperflow-editor-mcp-server.py` (Editor)
- `./agents/mcp-servers/broski-terminal-mcp-server.py` (Terminal)
- `./agents/mcp-config.json` (Configuration)

All three work together with cagent to give your agents full IDE control. 🔥
