FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install fastapi==0.115.5 uvicorn==0.32.0 prometheus-client==0.20.0 opentelemetry-api==1.27.0 opentelemetry-sdk==1.27.0 opentelemetry-exporter-otlp==1.27.0 opentelemetry-instrumentation-fastapi==0.48b0

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

COPY --chown=appuser:appuser main.py .

CMD ["python", "main.py"]
