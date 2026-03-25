FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy healer application code
COPY . /app/healer

# │ Phase 3 — copy shared agent modules so agents.shared is importable │
# Build context is agents/healer/ so we need shared copied in via compose
# We place it at /app/agents/shared to match the import path
RUN mkdir -p /app/agents/shared
COPY shared/ /app/agents/shared/

# Make agents a proper package
RUN touch /app/agents/__init__.py

# Set PYTHONPATH so both 'healer' and 'agents' are importable
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8008

# Run the application
CMD ["uvicorn", "healer.main:app", "--host", "0.0.0.0", "--port", "8008"]
