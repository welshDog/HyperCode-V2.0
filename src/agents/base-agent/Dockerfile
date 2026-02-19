# Base Dockerfile for all specialized agents
# Multi-stage build for optimal size and speed

FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Update PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Fix permissions
RUN chown -R appuser:appuser /home/appuser/.local

# Copy agent code
COPY --chown=appuser:appuser agent.py .
COPY --chown=appuser:appuser config/ ./config/

# Copy Hive Mind (shared memory/standards)
COPY --chown=appuser:appuser hive_mind/ ./hive_mind/

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

EXPOSE 8001

CMD ["python", "agent.py"]
