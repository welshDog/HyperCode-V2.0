import signal
from fastapi import FastAPI
import uvicorn
import os
import sys

app = FastAPI()

@app.get("/")
def read_root():
    return {"version": "v1.0", "message": "I am the test subject."}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Handle SIGTERM for graceful shutdown in Docker
def handle_sigterm(*args):
    print("Received SIGTERM, shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    # Listen on 0.0.0.0 is correct for Docker
    uvicorn.run(app, host="0.0.0.0", port=port)
