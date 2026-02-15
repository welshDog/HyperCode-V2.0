# 📘 HyperCode Operations Runbook

## 🚀 Deployment

### Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.20+
- 4GB RAM minimum available

### Start Sequence
1. **Pull Images**:
   ```bash
   docker-compose pull
   ```
2. **Start Core Services**:
   ```bash
   docker-compose up -d postgres redis hypercode-core
   ```
3. **Start Monitoring**:
   ```bash
   docker-compose up -d prometheus grafana
   ```
4. **Start Agents**:
   ```bash
   docker-compose up -d mcp-server coder-agent
   ```

### Verification Checks
- **Core API**: `curl http://localhost:8000/health` → `{"status": "ok"}`
- **Agent Connectivity**: Check logs for `Successfully connected to Docker MCP Server`
  ```bash
  docker-compose logs coder-agent | grep "MCP"
  ```
- **Grafana**: Access `http://localhost:3001`

## 🔄 Rollback

If a deployment fails:

1. **Stop Agents First**:
   ```bash
   docker-compose stop coder-agent mcp-server
   ```
2. **Revert Image Tags**:
   Edit `docker-compose.yml` to point to previous stable tags.
3. **Restart Stack**:
   ```bash
   docker-compose up -d
   ```

## 🚨 Incident Response

### High Memory Usage
If `coder-agent` consumes >512MB:
1. Check for orphaned containers spawned by the agent:
   ```bash
   docker ps --filter "label=managed_by=coder-agent"
   ```
2. Prune resources:
   ```bash
   docker system prune -f
   ```

### MCP Connection Failure
If agent logs show `MCP Client not initialized`:
1. Verify Docker socket mount:
   ```bash
   docker inspect hypercode-v20-coder-agent-1 | grep docker.sock
   ```
2. Restart MCP server:
   ```bash
   docker-compose restart mcp-server coder-agent
   ```

---
> *Built with WelshDog + BROski* 🚀🌙
