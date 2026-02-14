# Multi-purpose builder image for HyperCode project
# This image can be used for builds, tests, and CI/CD pipelines

FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (for any JS tooling)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install common Python tools
RUN pip install --no-cache-dir \
    pip-tools \
    wheel \
    setuptools \
    twine

WORKDIR /workspace

# ==================== Development Stage ====================
FROM base as development

# Install development tools
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    pytest-mock \
    black \
    ruff \
    mypy \
    ipython \
    debugpy \
    pre-commit

# Install Docker CLI for Docker-in-Docker scenarios
RUN curl -fsSL https://get.docker.com | sh

CMD ["/bin/bash"]

# ==================== Testing Stage ====================
FROM development as testing

# Install additional test dependencies
RUN pip install --no-cache-dir \
    faker \
    factory-boy \
    hypothesis \
    responses \
    freezegun \
    pytest-xdist \
    pytest-timeout

# Install performance testing tools
RUN npm install -g artillery

WORKDIR /tests

CMD ["pytest", "-v"]

# ==================== CI Stage ====================
FROM development as ci

# Install CI/CD specific tools
RUN pip install --no-cache-dir \
    coverage[toml] \
    pytest-html \
    pytest-json-report \
    bandit \
    safety

# Install code quality tools
RUN npm install -g \
    eslint \
    prettier \
    @commitlint/cli

# Install container scanning
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

WORKDIR /ci

CMD ["/bin/bash"]

# ==================== Documentation Builder ====================
FROM base as docs

# Install documentation tools
RUN pip install --no-cache-dir \
    mkdocs \
    mkdocs-material \
    mkdocstrings[python] \
    mkdocs-gen-files \
    mkdocs-literate-nav \
    mkdocs-section-index

WORKDIR /docs

CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]

# ==================== Database Migration ====================
FROM base as migration

# Install Prisma and migration tools
RUN pip install --no-cache-dir \
    prisma \
    alembic \
    sqlalchemy

WORKDIR /migrations

CMD ["prisma", "migrate", "deploy"]
