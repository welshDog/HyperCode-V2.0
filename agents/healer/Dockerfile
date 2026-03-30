FROM python:3.11-slim

# Install Docker CLI (not daemon, just the client tool)
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install python dependencies
# context is now ./agents, so requirements.txt is at healer/requirements.txt
COPY healer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy healer application code
COPY healer/ /app/healer

# Phase 3 — copy shared agent modules so agents.shared is importable
# context is ./agents so shared/ is directly accessible
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
