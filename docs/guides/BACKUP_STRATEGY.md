# 🛡️ HyperCode V2.0 - Backup Strategy & Disaster Recovery

This document outlines the comprehensive backup strategy for the HyperCode V2.0 repository, ensuring data integrity, availability, and disaster recovery readiness.

## 1. Repository Backup Protocol

### Primary Repository
- **Platform**: GitHub (Private Repository)
- **Structure**: Monorepo containing all source code, documentation, configurations, and deployment scripts.
- **Branch Protection**:
  - `main`: Protected branch. No direct pushes. Requires PR approval and passing CI checks.
  - `develop`: Protected branch. Requires passing CI checks.

### Mirroring & Snapshots
- **Local Mirror**: Maintain a full local clone with all branches and tags.
- **External Backup**: Periodic `git bundle` creation stored on secure external storage (S3/Drive).
- **Frequency**:
  - Automated GitHub backups (continuous).
  - Manual local snapshots before major version releases.

## 2. Data & Configuration Backup

### Environment Secrets
- **Policy**: `.env` files are NEVER committed.
- **Backup**: Encrypted copies of `.env.production` and API keys are stored in a secure password manager (e.g., 1Password, Vault).
- **Recovery**: Re-provision secrets from secure storage during deployment.

### Database (PostgreSQL)
- **Method**: `pg_dump` via Docker.
- **Script**: `scripts/backup_postgres.sh`
- **Schedule**: Daily automated backups.
- **Retention**: 7 days daily, 4 weeks weekly, 12 months monthly.

### Redis Persistence
- **Method**: RDB snapshots (dump.rdb).
- **Location**: Volume `redis-data`.
- **Strategy**: Docker volume backups.

## 3. Disaster Recovery Plan (DRP)

### Scenario A: GitHub Outage
1. **Access Local Mirror**: Use the latest local clone.
2. **Deploy from Local**: Use `docker-compose` to deploy directly from the local source.

### Scenario B: Accidental Repository Deletion
1. **Restore from Local**: Push the local mirror to a new repository.
   ```bash
   git remote set-url origin <new-repo-url>
   git push -u origin --all
   git push -u origin --tags
   ```
2. **Restore Secrets**: Re-apply environment variables.

### Scenario C: Corrupted Database
1. **Stop Services**: `docker-compose down`
2. **Restore Backup**: Use `scripts/restore_postgres.sh` with the latest valid dump.
3. **Verify Integrity**: Run health checks.

## 4. Verification Checklist

- [ ] **Codebase Integrity**: `git fsck --full` passes without errors.
- [ ] **CI/CD Pipelines**: All workflows (Build, Test, Security) are green.
- [ ] **Documentation**: README and Architecture docs are up-to-date.
- [ ] **Secret Availability**: All required keys are accessible in secure storage.
- [ ] **Backup Accessibility**: Verify access to the private repository and external backups.

## 5. Automation & CI/CD

- **Workflows**: Defined in `.github/workflows/`
  - `ci-cd.yml`: Main build and test pipeline.
  - `security.yml`: Code scanning and vulnerability checks.
  - `backup.yml`: (Planned) Automated backup verification.

---
**Maintained by**: HyperCode DevOps Team
**Last Updated**: 2026-02-17
