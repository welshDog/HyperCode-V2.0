"""test-agent FastAPI service."""

import logging
import os
import signal
import sys
import time
from collections.abc import Awaitable, Callable

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "msg": "%(message)s"}',
)
logger = logging.getLogger("test-agent")

app = FastAPI(title="test-agent", version="1.0.0")

START_TIME = time.time()


def _is_truthy(value: str | None) -> bool:
    """Return True if a string represents a truthy value."""
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def setup_telemetry() -> None:
    """Initialize OpenTelemetry tracing if enabled via environment."""
    if _is_truthy(os.getenv("OTEL_SDK_DISABLED")):
        logger.info("OpenTelemetry SDK is disabled.")
        return
    if _is_truthy(os.getenv("OTLP_EXPORTER_DISABLED")):
        logger.info("OpenTelemetry exporter is disabled.")
        return

    service_name = os.getenv("SERVICE_NAME", os.getenv("AGENT_ROLE", "test-agent"))
    environment = os.getenv("ENVIRONMENT", "development")
    endpoint = os.getenv("OTLP_ENDPOINT", "http://tempo:4317")

    resource = Resource.create(
        attributes={
            "service.name": service_name,
            "deployment.environment": environment,
        }
    )
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    )
    trace.set_tracer_provider(tracer_provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    logger.info("OpenTelemetry initialized for service: %s", service_name)


setup_telemetry()

PROM_REGISTRY = CollectorRegistry()
REQUESTS_TOTAL = Counter(
    "test_agent_requests_total",
    "Total requests received",
    ["method", "endpoint", "status"],
    registry=PROM_REGISTRY,
)
REQUEST_DURATION_SECONDS = Histogram(
    "test_agent_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
    registry=PROM_REGISTRY,
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)


@app.get("/")
def read_root():
    """Return basic identity information for this agent."""
    return {
        "version": "v1.0",
        "message": "I am the test subject.",
        "agent": os.getenv("AGENT_ROLE", "test-agent"),
        "core_url": os.getenv("CORE_URL", "not set"),
    }


@app.get("/health")
def health_check():
    """Return liveness information for Docker and service discovery."""
    try:
        uptime = round(time.time() - START_TIME, 2)
        return {"status": "ok", "uptime_seconds": uptime}
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return JSONResponse(
            status_code=500, content={"status": "error", "detail": str(e)}
        )


@app.get("/capabilities")
def capabilities():
    """Return a minimal capability descriptor for orchestration."""
    return {
        "name": "test-agent",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/capabilities", "/metrics"],
        "requires": ["hypercode-core"],
    }


@app.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus metrics for scraping."""
    return Response(generate_latest(PROM_REGISTRY), media_type=CONTENT_TYPE_LATEST)


@app.middleware("http")
async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Log requests and record Prometheus metrics."""
    start = time.time()
    response = await call_next(request)
    duration_seconds = time.time() - start
    duration_ms = round(duration_seconds * 1000, 2)
    endpoint = request.url.path
    REQUESTS_TOTAL.labels(
        method=request.method, endpoint=endpoint, status=str(response.status_code)
    ).inc()
    REQUEST_DURATION_SECONDS.labels(method=request.method, endpoint=endpoint).observe(
        duration_seconds
    )
    logger.info(
        "%s %s -> %s (%.2fms)",
        request.method,
        endpoint,
        response.status_code,
        duration_ms,
    )
    return response


def handle_sigterm(*_args: object) -> None:
    """Handle Docker SIGTERM for graceful shutdown."""
    logger.info("Received SIGTERM, shutting down gracefully...")
    sys.exit(0)


_ = signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    logger.info("test-agent starting on port %s", port)
    uvicorn.run(app, host="0.0.0.0", port=port)
