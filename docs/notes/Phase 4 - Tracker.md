# Phase 4 Tracker — Monitoring & Self-Healing

Owner: Lyndz  
Status: In progress  
Start date: 2026-03-11  
Target completion: 2026-03-14  

## Milestones

| Milestone | Target date | Status | Evidence link |
|---|---:|---|---|
| M1: Monitoring overlay boots | 2026-03-11 | ✅ Done | See M1 Evidence below |
| M2: Orchestrator metrics scraped + Grafana panels | 2026-03-12 | ✅ Done | See M2 Evidence below |
| M3: Healer watchdog running + failure injection passes SLA | 2026-03-13 | ✅ Done | See M3 Evidence below |
| M4: Alerts + runbook validated, phase signoff | 2026-03-14 | Not started | |

## Deliverables Checklist

### D1 — Monitoring overlay live
- [x] Start monitoring stack via docker compose (Prometheus + Grafana)
- [x] Confirm Prometheus UI reachable
- [x] Confirm Grafana UI reachable and Prometheus datasource exists

### D2 — Prometheus targets include crew-orchestrator
- [x] crew-orchestrator exposes `/metrics`
- [x] Prometheus scrapes crew-orchestrator `/metrics` and target is `UP`
- [x] `up{job="crew-orchestrator"}` is visible in Prometheus

### D3 — Grafana dashboard exists (Mission Control minimum)
- [x] Service health: `up` panel for core/orchestrator/agents
- [x] Smoke traffic: request rate panel (by result)
- [x] Smoke failures: failure rate panel
- [ ] Latency panel(s) if available

### D4 — Healer watchdog loop
- [x] Healer calls `/execute/smoke` on cadence with benchmark guardrails
- [x] Healer detection/remediation paths validated via failure injection
- [x] Remediation behavior defined and implemented (restart)

### D5 — Failure injection proof
- [x] Baseline: smoke passes on steady-state system
- [x] Force-kill an agent container
- [x] Detect within 90s and remediate within 5 minutes
- [x] Capture evidence bundle (metrics + timestamps + container events)

### D6 — Alerting and runbook
- [ ] Alert rules exist for target down + smoke failures + latency regression
- [ ] At least one alert is validated via controlled failure
- [ ] Rollback steps are documented and verified

## Daily Standup Log

### Date: 2026-03-11 (Evening — M1 Complete 🔥)
- Done:
  - Phase 4 kickoff docs created (plan + tracker + Healer Watchdog.md)
  - `/metrics` endpoint live at `http://127.0.0.1:8081/metrics` (200 OK)
  - `smoke_request_total` counter confirmed incrementing (0.0 → 1.0 on POST)
  - `smoke_redis_skip_total` confirmed at 1.0 (zero audit leakage verified)
  - M1 evidence bundle committed to tracker
  - D1 + D2 deliverables fully checked off
- Next:
  - Bring up monitoring stack: `docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d`
  - Verify Prometheus scrapes crew-orchestrator (check `http://127.0.0.1:9090/targets`)
  - Add Grafana smoke dashboard panels (D3)
- Blockers: None
- Evidence captured: Full `/metrics` output + POST response in M1 Evidence section below

### Date: YYYY-MM-DD
- Done:
- Next:
- Blockers:
- Evidence captured:

## M2 Evidence (Prometheus Scrape + Grafana Panels)

Timestamp (UTC): 2026-03-11T23:30:17Z  
Executed by: Trae IDE automation (GPT-5.2)  

### Container + health verification

All required Phase 4 containers are running and healthy:

- `hypercode-core` -> 200 OK `http://127.0.0.1:8000/health`
- `crew-orchestrator` -> 200 OK `http://127.0.0.1:8081/health`
- `healer-agent` -> 200 OK `http://127.0.0.1:8010/health`
- `prometheus` -> 200 OK `http://127.0.0.1:9090/-/ready`
- `grafana` -> 200 OK `http://127.0.0.1:3001/api/health`

Smoke counters are present on orchestrator metrics:

```text
smoke_request_total{mode="noop",result="pass"} 1.0
smoke_redis_skip_total 11.0
```

### Prometheus scrape target validation

Prometheus target `job="crew-orchestrator"` is `UP` and scraping `/metrics`:

```json
{
  "scrapeUrl": "http://crew-orchestrator:8080/metrics",
  "health": "up",
  "lastError": ""
}
```

### Grafana provisioning validation

Grafana provisioning logs confirm dashboards + alerting provisioning completed:

```text
logger=provisioning.alerting ... msg="starting to provision alerting"
logger=provisioning.alerting ... msg="finished to provision alerting"
logger=provisioning.dashboard ... msg="starting to provision dashboards"
logger=provisioning.dashboard ... msg="finished to provision dashboards"
```

Dashboard file (provisioned):
- `monitoring/grafana/provisioning/dashboards/smoke_metrics_dashboard.json`

## M3 Evidence (Healer Watchdog + Failure Injection)

Timestamp (UTC): 2026-03-12T01:37:33Z  
Executed by: Trae IDE automation (GPT-5.2)  

### Test target

- Target agent container: `backend-specialist`
- Failure injection: `docker kill backend-specialist` with restart policy temporarily set to `no` (prevents Docker auto-restart so remediation requires the watchdog)
- Detection signal: `smoke_request_total{mode="probe_health",result="fail"}` counter increment on `crew-orchestrator /metrics`

### SLA results (pass)

- Baseline UTC: `2026-03-12T01:37:36.7686543Z`
- Kill UTC: `2026-03-12T01:37:39.1516728Z`
- Detect UTC: `2026-03-12T01:37:48.4612594Z`
- Recovered UTC: `2026-03-12T01:37:55.7950974Z`
- Detection latency: `9.3s` (≤ 90s ✅)
- Remediation time: `7.3s` (≤ 300s ✅)

### Evidence archive

Evidence directory:
- `artifacts/phase4/m3_evidence_20260312T013733Z`

Key files:
- `summary.json` (computed SLA results)
- `baseline_backend_specialist_state.txt` (pre-failure container health)
- `kill_utc.txt`, `detect_utc.txt`, `recovered_utc.txt` (timestamps)
- `metrics_baseline.txt`, `metrics_post_lines.txt` (detection counter evidence)
- `docker_events_backend_specialist.txt` (container event record)

## M1 Evidence (Prometheus Metrics Integration)

Timestamp (UTC): 2026-03-11T19:33:09Z  
Executed by: Trae IDE automation (GPT-5.2)  

### Step 1: Verify `/metrics` is operational and exposes smoke counters

Command:

```powershell
curl http://127.0.0.1:8081/metrics | Select-String "smoke_request_total"
```

Output:

```text
# HELP smoke_request_total Total /execute/smoke requests
# TYPE smoke_request_total counter
smoke_request_total{mode="noop",result="pass"} 0.0
```

### Step 3: Generate a smoke request and confirm counter increments

Command:

```powershell
curl -X POST http://127.0.0.1:8081/execute/smoke `
  -H "Content-Type: application/json" `
  -H "X-API-Key: <BENCH_KEY>" `
  -H "X-Smoke-Mode: true" `
  -d '{"mode":"noop"}'
```

Output:

```json
{"smoke":"pass","mode":"noop","latency_ms":0.14,"redis_writes_skipped":1,"approval_skipped":true,"agent":null,"agent_http_status":null,"agent_latency_ms":null,"healthy":null,"total":null,"agents":null,"timestamp":"2026-03-11T19:32:31.479514+00:00"}
```

Command:

```powershell
curl http://127.0.0.1:8081/metrics | Select-String "smoke_request"
```

Output:

```text
# HELP smoke_request_total Total /execute/smoke requests
# TYPE smoke_request_total counter
smoke_request_total{mode="noop",result="pass"} 1.0
# HELP smoke_request_created Total /execute/smoke requests
# TYPE smoke_request_created gauge
smoke_request_created{mode="noop",result="pass"} 1.773257430187753e+09
```

### Step 5: Full `/metrics` output captured for sign-off

```text
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 1044.0
python_gc_objects_collected_total{generation="1"} 176.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable objects found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 190.0
python_gc_collections_total{generation="1"} 17.0
python_gc_collections_total{generation="2"} 1.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="11",patchlevel="8",version="3.11.8"} 1.0
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
process_virtual_memory_bytes 3.91888896e+08
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 7.7348864e+07
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
process_start_time_seconds 1.77325742575e+09
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 3.95
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
process_open_fds 17.0
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
process_max_fds 1.048576e+06
# HELP smoke_request_total Total /execute/smoke requests
# TYPE smoke_request_total counter
smoke_request_total{mode="noop",result="pass"} 1.0
# HELP smoke_request_created Total /execute/smoke requests
# TYPE smoke_request_created gauge
smoke_request_created{mode="noop",result="pass"} 1.773257430187753e+09
# HELP smoke_redis_skip_total Redis writes skipped by smoke endpoint
# TYPE smoke_redis_skip_total counter
smoke_redis_skip_total 1.0
# HELP smoke_redis_skip_created Redis writes skipped by smoke endpoint
# TYPE smoke_redis_skip_created gauge
smoke_redis_skip_created 1.7732574301876109e+09
```

## Blockers Log

| Date | Blocker | Owner | Mitigation | ETA |
|---|---|---|---|---:|
|  |  |  |  |  |

## Evidence Bundle Index

Add links/paths as they are produced:

- Smoke reports: `artifacts/smoke/`
- Load test results (if run): `artifacts/load/`
- Grafana exports: `monitoring/grafana/` or exported JSON file path
- Incident/failure injection log: (path)
