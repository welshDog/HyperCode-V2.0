# Changelog

> **built with WelshDog + BROski 🚀🌙**

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Evolutionary Pipeline:** Implemented self-improvement capabilities allowing agents to request infrastructure updates programmatically.
    - **Evolution Protocol:** Standardized `ImprovementRequest` schema and validation.
    - **DevOps Listener:** Autonomous deployment execution by the DevOps agent.
    - **Deployer Tool:** Shared utility for container rebuilding and rolling updates.
- **Dashboard Stability:** Enhanced `hypercode-dashboard` with robust health checks and E2E tests.
- **Test Agent:** Added a dedicated test subject (`test-agent`) for verifying evolutionary cycles.
- **Security Documentation:** Added `DEVOPS_PERMISSIONS.md` and `EVOLUTIONARY_PIPELINE_SETUP.md`.
- **MCP Integration:** Full support for Model Context Protocol to enable standardized agent tooling.
- **Autonomous Operations:** Agents can now deploy and manage Docker containers dynamically.
- **Observability Stack:** Integrated Prometheus, Grafana, and AlertManager for real-time monitoring.
- **Documentation:** Comprehensive architecture, security, and onboarding guides.
- **Traceability:** Matrix mapping requirements to code and tests.
- **New Quickstart:** Added `docs/QUICKSTART.md` and updated `.env.example`.

### Changed
- **Dashboard Health Check:** Increased `start_period` to 60s and switched to `wget --spider` to prevent restart loops.
- **Docker Compose:** Updated `devops-engineer` permissions to include Docker socket access for evolution capabilities.
- **Documentation Overhaul:** Synchronized all `docs/` files with Main `README.md` (Docker Compose syntax, ports, env setup).
- **Agent Architecture:** Refactored `Coder Agent` to use MCP clients instead of direct shell execution.
- **Docker Compose:** Updated service definitions to support new microservices structure.

### Fixed
- **Dashboard Crash Loop:** Resolved Next.js binding issue (was listening on internal IP, health check probing localhost) by setting `HOSTNAME=0.0.0.0`.
- **Docker Socket Mounting:** Resolved permission issues on Windows/Linux cross-compatibility.
- **Database Migrations:** Fixed race conditions during initial startup.
- **Ollama Health Check:** Fixed health check failure by switching to TCP probe.

## [2.0.0] - 2026-01-15

### Initial Release
- Core microservices architecture.
- Basic Coder Agent capabilities.
- Next.js Frontend and FastAPI Backend.

---
> **built with WelshDog + BROski 🚀🌙**
