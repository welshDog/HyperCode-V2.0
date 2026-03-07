# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# gcc/g++ needed for some python packages
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/

# Config poetry to not use virtualenvs
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --without dev --no-interaction --no-ansi --no-root

# Copy the rest of the code
COPY . /app

# Expose ports (8000 for API)
EXPOSE 8000

# Default command (can be overridden)
# Run API by default, or use "python -m src.main run" for bot
ENV PYTHONPATH=/app
CMD ["python", "src/main.py", "run"]
