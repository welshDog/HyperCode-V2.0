# Enterprise Hardening Roadmap

**Status:** 🟡 In Progress  
**Last Updated:** 2026-02-20

This roadmap outlines the steps to take HyperCode V2.0 from "Functional Prototype" to "Enterprise-Grade Platform".

## Phase 1: Security & Infrastructure (✅ COMPLETED)
- [x] Fix insecure defaults in `docker-compose`.
- [x] Pin Docker image versions.
- [x] Remove source code mounts in production.
- [x] Add `SECURITY.md`.
- [x] Fix exception swallowing in core code.
- [x] Upgrade to Gunicorn for production concurrency.

## Phase 2: Observability & Resilience (Next)
- [ ] **Centralized Logging**: Ship logs to Loki or external ELK stack.
- [ ] **Alerting**: Configure AlertManager with Slack/PagerDuty receivers (using `alert.rules.yml`).
- [ ] **Rate Limiting**: Tune Redis-backed rate limiting in `hypercode-core`.
- [ ] **Disaster Recovery**: Automated Postgres backups to S3/AWS.

## Phase 3: Testing & QA
- [ ] **Unit Test Coverage**: Increase core coverage to >80%.
- [ ] **Integration Tests**: Add more scenarios to `tests/framework`.
- [ ] **Load Testing**: Run Locust tests in CI pipeline.

## Phase 4: Developer Experience
- [ ] **CLI Tool**: Enhance `hypercode-cli` for easier management.
- [ ] **Plugin System**: Formalize the agent plugin architecture.
- [ ] **Documentation**: Generate API client SDKs automatically.
