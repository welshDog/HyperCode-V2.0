-- HyperHealth DB schema
-- Run once against your existing hypercode postgres DB

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Check Definitions ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS check_definitions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                TEXT NOT NULL,
    type                TEXT NOT NULL,  -- http, db, cache, tls, cpu, etc.
    target              TEXT NOT NULL,  -- URL, DSN, host:port
    environment         TEXT NOT NULL DEFAULT 'prod',  -- blue, green, prod, staging
    interval_seconds    INT  NOT NULL DEFAULT 30,
    thresholds          JSONB,
    alert_policy_id     INT,
    self_heal_policy_id INT,
    tags                TEXT[] DEFAULT '{}',
    enabled             BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_checks_env      ON check_definitions(environment);
CREATE INDEX IF NOT EXISTS idx_checks_type     ON check_definitions(type);
CREATE INDEX IF NOT EXISTS idx_checks_enabled  ON check_definitions(enabled);

-- ─── Check Results ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS check_results (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    check_id     UUID NOT NULL REFERENCES check_definitions(id) ON DELETE CASCADE,
    status       TEXT NOT NULL,  -- OK, WARN, CRIT, UNKNOWN
    latency_ms   FLOAT,
    value        FLOAT,
    message      TEXT,
    environment  TEXT NOT NULL DEFAULT 'prod',
    started_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_results_check_id   ON check_results(check_id);
CREATE INDEX IF NOT EXISTS idx_results_started_at ON check_results(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_results_status      ON check_results(status);

-- ─── Incidents ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS incidents (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    check_id     UUID REFERENCES check_definitions(id),
    title        TEXT NOT NULL,
    summary      TEXT,
    severity     TEXT NOT NULL DEFAULT 'warn',  -- info, warn, crit
    environment  TEXT NOT NULL DEFAULT 'prod',
    service      TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_incidents_env         ON incidents(environment);
CREATE INDEX IF NOT EXISTS idx_incidents_resolved    ON incidents(resolved_at);
CREATE INDEX IF NOT EXISTS idx_incidents_severity    ON incidents(severity);

-- ─── Self-Heal Policies ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS self_heal_policies (
    id                        SERIAL PRIMARY KEY,
    name                      TEXT NOT NULL,
    enabled                   BOOLEAN NOT NULL DEFAULT TRUE,
    trigger_status            TEXT NOT NULL DEFAULT 'CRIT',
    trigger_count             INT NOT NULL DEFAULT 3,
    trigger_window_seconds    INT NOT NULL DEFAULT 120,
    action                    TEXT NOT NULL,
    action_params             JSONB DEFAULT '{}',
    max_retries_per_hour      INT NOT NULL DEFAULT 3,
    require_human_approval    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Seed: default HyperCode checks ─────────────────────────────────────────
INSERT INTO check_definitions (name, type, target, environment, interval_seconds, thresholds, tags)
VALUES
    ('hypercode-core',       'http',  'http://hypercode-core:8000/health',        'prod', 15, '{"latency_ms":{"warn":300,"crit":1000}}'::jsonb, ARRAY['core']),
    ('healer-agent',         'http',  'http://healer-agent:8008/health',          'prod', 15, '{"latency_ms":{"warn":300,"crit":1000}}'::jsonb, ARRAY['agent']),
    ('crew-orchestrator',    'http',  'http://crew-orchestrator:8080/health',     'prod', 20, '{"latency_ms":{"warn":500,"crit":2000}}'::jsonb, ARRAY['agent']),
    ('mission-control',      'http',  'http://hypercode-dashboard:8088/health',   'prod', 30, '{"latency_ms":{"warn":500,"crit":2000}}'::jsonb, ARRAY['dashboard']),
    ('postgres-db',          'db',    'postgresql://hypercode:hypercode@postgres:5432/hypercode', 'prod', 30, '{"latency_ms":{"warn":100,"crit":500}}'::jsonb, ARRAY['infra']),
    ('redis-cache',          'cache', 'redis://redis:6379/0',                     'prod', 15, '{"latency_ms":{"warn":20,"crit":100}}'::jsonb,  ARRAY['infra'])
ON CONFLICT DO NOTHING;
