import signal
import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "msg": "%(message)s"}',
)
logger = logging.getLogger("test-agent")

app = FastAPI(title="test-agent", version="1.0.0")

START_TIME = time.time()
def read_root():
    return {"version": "v1.0", "message": "I am the test subject."}

    return {
        "version": "v1.0",
        "message": "I am the test subject.",
        "agent": os.getenv("AGENT_ROLE", "test-agent"),
        "core_url": os.getenv("CORE_URL", "not set"),
    }
def health_check():
    return {"status": "ok"}

    try:
        uptime = round(time.time() - START_TIME, 2)
        return {"status": "ok", "uptime_seconds": uptime}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

@app.get("/capabilities")
def capabilities():
    return {
        "name": "test-agent",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/capabilities"],
        "requires": ["hypercode-core"],
    }

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration}ms)")
    return response
def handle_sigterm(*args):
    sys.exit(0)
    logger.info("Received SIGTERM, shutting down gracefully...")
signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    # Listen on 0.0.0.0 is correct for Docker
    uvicorn.run(app, host="0.0.0.0", port=port)
    logger.info(f"test-agent starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
