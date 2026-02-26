from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import settings
from app.core.telemetry import setup_telemetry
import logging
import time

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="HyperCode Core API Service",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenTelemetry
setup_telemetry(app)

# Prometheus Instrumentation
instrumentator = Instrumentator().instrument(app).expose(app)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
async def root():
    return {"message": "Welcome to HyperCode Core API"}

# Example Endpoint for Custom Tracing
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@app.get("/api/v1/trace-example")
async def trace_example():
    with tracer.start_as_current_span("custom_operation") as span:
        span.set_attribute("custom.attribute", "example_value")
        logger.info("Performing a traced operation")
        time.sleep(0.1)  # Simulate work
        with tracer.start_as_current_span("inner_operation"):
            logger.info("Inside inner operation")
            time.sleep(0.05)
    return {"message": "Traced operation completed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
