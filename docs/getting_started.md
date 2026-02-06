# Getting Started with HyperCode V2.0

> **built with WelshDog + BROski 🚀🌙**

Welcome to HyperCode V2.0! This guide will take you from `git clone` to your first "Hello World" deployment.

## Prerequisites

- **Docker & Docker Compose:** Ensure Docker Desktop is running.
- **Git:** For version control.
- **Node.js (v18+) & Python (3.10+):** For local development tools.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/HyperCode-V2.0.git
   cd HyperCode-V2.0
   ```

2. **Environment Setup**
   Copy the example environment files:
   ```bash
   cp .env.example .env
   ```
   *Note: Update the `.env` file with your specific configuration (API keys, database credentials) if necessary.*

3. **Start the Stack**
   Use the provided runbook command to start all services:
   ```bash
   docker-compose up -d --build
   ```

4. **Verify Installation**
   Check if all containers are running:
   ```bash
   docker-compose ps
   ```
   You should see `hypercode-core`, `postgres`, `redis`, `mcp-server`, and observability containers up.

## Hello World Walkthrough

1. **Access the Interface**
   Open your browser and navigate to `http://localhost:3000` (or the port configured for the frontend).

2. **Trigger a Simple Task**
   - Log in (default admin credentials in `.env`).
   - Navigate to the "Agents" tab.
   - Select "Coder Agent".
   - Input: "Create a Python script that prints 'Hello, HyperCode!'".

3. **Observe Execution**
   - Watch the agent analyze the request.
   - See the code generation.
   - Confirm the execution output in the logs.

## Common Issues

- **Docker Socket Permissions:** If the agent fails to start containers, ensure the Docker socket is correctly mounted and permissions are set (see `docs/MCP_INTEGRATION.md`).
- **Database Connection:** If `hypercode-core` fails, check if `postgres` is healthy.

## Next Steps

- Review the [Architecture](architecture.md) to understand the system.
- Check the [API Reference](api_reference.md) for integration details.

---
> **built with WelshDog + BROski 🚀🌙**
