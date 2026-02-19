# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Hyper AI File System (HAFS)**: A comprehensive, neurodivergent-friendly file system architecture.
    - **Reactive Watcher**: `scripts/hafs/watcher.py` monitors file changes in real-time.
    - **Context Walker**: `scripts/hafs/walker.py` provides context-aware navigation and predictive file suggestions.
    - **Semantic Search**: Integrated ChromaDB and `sentence-transformers` for vector-based code search (`scripts/hafs/embeddings.py`).
    - **API Server**: FastAPI service (`scripts/hafs/server.py`) exposing HAFS capabilities to agents.
    - **Self-Correction**: `scripts/hafs/corrector.py` allows agents to diagnose errors using semantic search.
    - **Auto-Documentation**: `scripts/hafs/documenter.py` generates markdown docs based on code analysis.
    - **Visualization**: Interactive D3.js graph of the codebase (`docs/design/hafs_graph.html`).
- **Scripts**:
    - `scripts/organize_repo.py`: Utility to reorganize the repository into the new taxonomy.
    - `scripts/start_hafs.py`: Entry point for the HAFS watcher.
    - `scripts/query_hafs.py`: CLI tool for querying context and semantic search.
    - `scripts/view_graph.py`: Simple server to view the neural graph.
- **Documentation**:
    - `docs/design/HYPER_AI_FILE_SYSTEM.md`: Comprehensive design document.
    - `docs/guides/HAFS_USER_GUIDE.md`: User guide for HAFS tools.
    - `.ai/MASTER_INDEX.json`: Real-time index of the repository.
    - `.ai/PROJECT_CONTEXT.md`: System prompt context for LLMs.

### Changed
- **Repository Structure**: Reorganized root directory to reduce entropy.
    - Moved reports to `docs/reports/`.
    - Moved design docs to `docs/design/`.
    - Moved guides to `docs/guides/`.
    - Archived deprecated files in `archive/`.
- **Frontend Configuration**: Updated `broski-terminal/tsconfig.json` to include `node` types, resolving linter errors.

### Fixed
- **Linter Errors**: Resolved `Cannot find name 'process'` in `useSwarmData.ts`, `useWebSocket.ts`, and `page.tsx` by updating TypeScript configuration.
