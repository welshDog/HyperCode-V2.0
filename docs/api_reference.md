# API Reference

> **built with WelshDog + BROski 🚀🌙**

This document describes the core REST API endpoints for HyperCode V2.0.

**Interactive Documentation:**
For real-time testing and schema details, visit the Swagger UI:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

## Base URL
`http://localhost:8000/api/v1`

## Endpoints

### Health Check
**GET** `/health`
- **Description:** Returns the system health status.
- **Response:**
  ```json
  {
    "status": "healthy",
    "version": "2.1.0",
    "services": {
      "database": "up",
      "redis": "up"
    }
  }
  ```

### Agents

#### List Agents
**GET** `/agents`
- **Description:** Retrieves a list of available agents.
- **Response:** `200 OK` - Array of Agent objects.

#### Deploy Agent
**POST** `/agents/{agent_id}/deploy`
- **Description:** Triggers an agent deployment task.
- **Body:**
  ```json
  {
    "task": "string",
    "context": {}
  }
  ```
- **Response:** `202 Accepted` - Task ID.

### Execution

## WebSocket API (Bridge Server)

The Bridge Server provides a real-time WebSocket interface for agents and clients.

**Endpoint:** `ws://localhost:8001/ws/bridge`

### Message Types

#### 1. Ping/Pong (Heartbeat)
Keep connections alive.
- **Client:** `{"type": "ping"}`
- **Server:** `{"type": "pong"}`

#### 2. Context Ingestion
Submit documentation or code context to the Weaver Agent.
- **Client Request:**
  ```json
  {
    "type": "ingest",
    "id": "req_123",
    "context_type": "documentation",
    "content": "# Markdown Content..."
  }
  ```
- **Server Response (Ack):**
  ```json
  {
    "type": "ack",
    "request_id": "req_123",
    "status": "success",
    "entry_id": "uuid-entry-id",
    "message": "Optional status message"
  }
  ```

#### 3. Task Updates (Broadcast)
Real-time updates from agents.
- **Server Broadcast:**
  ```json
  {
    "type": "task_update",
    "payload": { ... },
    "timestamp": "2026-02-20T10:00:00Z"
  }
  ```


#### Get Execution Status
**GET** `/executions/{execution_id}`
- **Description:** Gets the status and logs of a specific task execution.
- **Response:**
  ```json
  {
    "id": "uuid",
    "status": "running|completed|failed",
    "logs": ["..."]
  }
  ```

## Error Handling
Standard HTTP status codes are used:
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

---
> **built with WelshDog + BROski 🚀🌙**
