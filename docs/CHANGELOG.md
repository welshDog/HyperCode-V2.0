# Changelog

> **built with WelshDog + BROski 🚀🌙**

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **MCP Integration:** Full support for Model Context Protocol to enable standardized agent tooling.
- **Autonomous Operations:** Agents can now deploy and manage Docker containers dynamically.
- **Observability Stack:** Integrated Prometheus, Grafana, and AlertManager for real-time monitoring.
- **Documentation:** Comprehensive architecture, security, and onboarding guides.
- **Traceability:** Matrix mapping requirements to code and tests.
- **New Quickstart:** Added `docs/QUICKSTART.md` and updated `.env.example`.

### Changed
- **Documentation Overhaul:** Synchronized all `docs/` files with Main `README.md` (Docker Compose syntax, ports, env setup).
- **Agent Architecture:** Refactored `Coder Agent` to use MCP clients instead of direct shell execution.
- **Docker Compose:** Updated service definitions to support new microservices structure.

### Fixed
- **Docker Socket Mounting:** Resolved permission issues on Windows/Linux cross-compatibility.
- **Database Migrations:** Fixed race conditions during initial startup.
- **Ollama Health Check:** Fixed health check failure by switching to TCP probe.

## [2.1.0] - 2026-02-20

### Added
- **Bridge Server:** Dedicated WebSocket server (`ws://localhost:8001/ws/bridge`) for real-time agent communication.
- **Weaver Agent:** Advanced context ingestion system using ChromaDB for semantic search and knowledge management.
- **Batch Ingestion:** Weaver now supports `ingest_batch` with rate limiting and error handling.
- **WebSocket Protocol:** New `ingest` message type for direct documentation/context submission from clients.
- **Frontend Integration:** `broski-terminal` now connects to Bridge Server with automatic reconnection.
- **Documentation Utility:** Added `ingest_docs.py` script for bulk documentation processing.

### Changed
- **Architecture:** Decoupled WebSocket logic into standalone Bridge Server for better scalability.
- **API Reference:** Updated with WebSocket protocol details and message formats.
- **Nexus Integration:** Enhanced documentation for Weaver's vector database capabilities.

## [2.0.0] - 2026-01-15

### Initial Release
- Core microservices architecture.
- Basic Coder Agent capabilities.
- Next.js Frontend and FastAPI Backend.

---
> **built with WelshDog + BROski 🚀🌙**
