# Frontend Specialist Agent
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY agent.py .
COPY config.json .

# Mount point for Hive Mind
VOLUME ["/app/hive_mind"]

ENV AGENT_NAME=frontend-specialist
ENV AGENT_ROLE="Frontend Specialist"
ENV AGENT_MODEL=claude-3-5-sonnet-20241022
ENV AGENT_PORT=8002

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8002/health')" || exit 1

EXPOSE 8002

CMD ["python", "agent.py"]
