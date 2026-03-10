# Changelog

> **built with WelshDog + BROski 🚀🌙**

**Doc Tag:** v2.0.0 | **Last Updated:** 2026-03-10

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository report for community visibility: [REPOSITORY_REPORT.md](REPOSITORY_REPORT.md)
- Documentation audit + sync checklist:
  - [docs/DOC_AUDIT_REPORT.md](docs/DOC_AUDIT_REPORT.md)
  - [docs/DOCS_SYNC_CHECKLIST.md](docs/DOCS_SYNC_CHECKLIST.md)
- Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

### Changed
- SQLAlchemy Base migrated to `DeclarativeBase` with SQLAlchemy 2.0 typed models (`Mapped[]`, `mapped_column`).
- Local-first LLM defaults (TinyLlama-first) with auto model selection and tuned generation options.
- Backend documentation links standardized to repo-relative paths.

### Fixed
- Test suite stability improved via deterministic mocks and reduced external side effects during imports.

## [2.0.0] - 2026-01-15

### Initial Release
- Core microservices architecture.
- Basic Coder Agent capabilities.
- Next.js Frontend and FastAPI Backend.

---
> **built with WelshDog + BROski 🚀🌙**
