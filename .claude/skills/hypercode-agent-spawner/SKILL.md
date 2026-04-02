---
name: hypercode-agent-spawner
description: Spawns, configures, and registers new HyperCode agents into the Crew Orchestrator. Use when user asks to create a new agent, add a specialist to the system, or when Agent X needs to deploy a new capability. Handles agent spec creation, Docker service wiring, and Redis pub/sub registration automatically.
---

# HyperCode Agent Spawner

## Quick spawn

```bash
python scripts/spawn_agent.py --name <agent-name> --role <role> --port <port>
```

## Agent spec template

Every agent MUST have these fields in its spec JSON:

```json
{
  "name": "agent-name",
  "role": "specialist description",
  "port": 8XXX,
  "tools": ["tool1", "tool2"],
  "memory": "redis|postgres|none",
  "safety_level": "strict|moderate|open",
  "auto_evolve": true
}
```

## Steps to spawn

1. Validate name is unique: `python scripts/spawn_agent.py --check-name <name>`
2. Generate spec file → saves to `agents/<name>/agent_spec.json`
3. Create FastAPI service stub → `agents/<name>/main.py`
4. Register in Crew Orchestrator via Redis: channel `hypercode:agents:register`
5. Add to `docker-compose.hyper-agents.yml`
6. Health check: `curl http://localhost:<port>/health`

## Advanced details

**Agent Teams** (Claude Opus 4.6 style): See [AGENT_TEAMS.md](AGENT_TEAMS.md)
**Safety limits**: See [SAFETY.md](SAFETY.md)
