# Contributing to HyperCode V2.0

Welcome to the HyperCode project! We're building the future of neurodivergent-first AI development tools. This guide will help you get started.

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/hypercode-v2.git
   cd hypercode-v2
   ```

2. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the Platform**
   ```bash
   # Start core services
   docker-compose up -d

   # Start with agents
   docker-compose --profile agents up -d

   # Start with monitoring (Prometheus, Grafana, Jaeger)
   docker-compose --profile monitoring up -d

   # Start production stack (includes Nginx Gateway)
   docker-compose --profile production --profile agents --profile monitoring up -d
   ```

### Verifying the Launch
To validate your deployment, run the verification script (PowerShell):
```powershell
# Requires production profile for full check
./scripts/verify_launch.ps1
```

## �️ Development Workflow

### Project Structure
- `THE HYPERCODE/`: Core platform code
- `agents/`: AI agent definitions
- `BROski Business Agents/`: Frontend terminal
- `docs/`: Documentation

### Coding Standards
- **Python**: Follow PEP 8. Use `black` and `ruff` for formatting.
- **JavaScript/TypeScript**: Use `prettier` and `eslint`.
- **Commits**: Use Conventional Commits (e.g., `feat: add new agent`, `fix: resolve docker loop`).

### Testing
Run the test suite before submitting PRs:
```bash
# Run core tests
docker-compose --profile agents run hypercode-core pytest

# Run agent tests
# (Check specific agent directories)
```

## 🐛 Troubleshooting

### Common Issues
- **Docker Loops/Conflicts**: Ensure you aren't running multiple compose files. Use `docker-compose.yml` with profiles.
- **Port Conflicts**: Check if ports 8000, 3000, 5432, or 6379 are in use.
- **Health Checks**: If a service is unhealthy, check logs: `docker-compose logs <service_name>`.

### Reporting Issues
Please use the GitHub Issue Tracker. Include:
- Steps to reproduce
- Expected vs. actual behavior
- Logs/Screenshots

## 🤝 Pull Request Process
1. Fork the repo and create a branch (`feature/your-feature`).
2. Commit your changes.
3. Push to your fork and open a PR.
4. Wait for code review and CI checks.

Thank you for contributing! 🚀
