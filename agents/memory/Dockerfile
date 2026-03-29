# agents/memory/Dockerfile
# Python FastAPI memory agent — shared key/value store for HyperCode agents.

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PORT=8082 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8082

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:8082/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]
