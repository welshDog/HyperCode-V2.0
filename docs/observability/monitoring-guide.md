# 👁️ Observability & Monitoring Guide

HyperCode V2.0 features an enterprise-grade observability stack built on **Prometheus**, **Grafana**, **Jaeger**, **Loki**, and **Tempo**.

> **Dashboards**
> *   **Grafana**: [http://localhost:3001](http://localhost:3001) (User: `admin` / Pass: `admin`)
> *   **Prometheus**: [http://localhost:9090](http://localhost:9090)
> *   **Jaeger**: [http://localhost:16686](http://localhost:16686)

## 1. Metrics (Prometheus)

The system automatically scrapes metrics from all core services.

### Key Targets
*   `hypercode-core:8000` (FastAPI Application Metrics)
*   `celery-exporter:9808` (Celery Worker Metrics)
*   `minio:9000` (Object Storage Metrics)
*   `node-exporter:9100` (Host System Metrics)
*   `cadvisor:8080` (Container Metrics)

### Dashboard Highlights
*   **HyperStation Mission Control**: Real-time view of active agents, tasks, and system health.
*   **Prometheus 2.0 Overview**: Deep dive into scrape targets and time series data.
*   **Celery Overview**: Task success/failure rates, queue depth, and worker status.

## 2. Logs (Loki & Promtail)

Logs are aggregated centrally using **Loki**.

### Accessing Logs
Use the **Explore** tab in Grafana and select `Loki` as the datasource.

**Query Example:**
```logql
{container_name="hypercode-core"} |= "error"
```

## 3. Tracing (Jaeger & Tempo)

Distributed tracing allows you to visualize the flow of requests through the system.

### Instrumentation
The backend is instrumented with **OpenTelemetry** (`opentelemetry-instrumentation-fastapi`).

### Viewing Traces
1.  Go to **Grafana Explore**.
2.  Select `Tempo`.
3.  Search for `service_name="hypercode-core"`.
4.  Click on a trace ID to see the full waterfall.

## 4. Troubleshooting Observability

**"Celery Worker Down in Prometheus"**
Ensure the `celery-exporter` container is running:
```powershell
docker compose up -d celery-exporter
```

**"No Host Disk Usage"**
This is a known issue on Windows/WSL2 due to Docker mount path limitations.

**"Missing Application Metrics"**
Verify the metrics endpoint is reachable:
```powershell
docker exec hypercode-core curl -s http://localhost:8000/metrics
```
