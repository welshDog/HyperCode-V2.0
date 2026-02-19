# 🚀 HyperCode Agent Crew - Quick Setup

## Fastest Way to Start

### Windows
```cmd
.\scripts\start-agents.bat
```

### Linux/Mac
```bash
chmod +x scripts/start-agents.sh
./scripts/start-agents.sh
```

## Manual Setup

1. **Copy environment file:**
   ```bash
   cp .env.agents.example .env.agents
   ```

2. **Add your Anthropic API key:**
   Edit `.env.agents` and replace `your_anthropic_api_key_here` with your actual key

3. **Start the crew:**
   ```bash
   docker-compose -f docker-compose.agents.yml --env-file .env.agents up -d
   ```

## Access Points

- **Orchestrator API:** http://localhost:8080
- **Agent Dashboard:** http://localhost:8090
- **API Documentation:** http://localhost:8080/docs

## Quick Test

```bash
# Check all agents are healthy
curl http://localhost:8080/agents/status

# Plan a feature
curl -X POST http://localhost:8080/plan \
  -H "Content-Type: application/json" \
  -d '{"task": "Create a user authentication system"}'
```

## Common Commands

```bash
# View logs
docker-compose -f docker-compose.agents.yml logs -f

# Stop agents
docker-compose -f docker-compose.agents.yml down

# Restart single agent
docker-compose -f docker-compose.agents.yml restart frontend-specialist

# Check resource usage
docker stats
```

## Troubleshooting

**Agents not starting?**
- Check Docker Desktop is running
- Verify your API key in `.env.agents`
- Check logs: `docker-compose -f docker-compose.agents.yml logs`

**Port conflicts?**
- Edit `docker-compose.agents.yml` to change ports
- Default ports: 8080 (orchestrator), 8001-8008 (agents), 8090 (dashboard)

For full documentation, see `agents/README.md`
