FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into package structure
# We copy current directory (.) to /app/healer
COPY . /app/healer

# Set PYTHONPATH so 'healer' is importable
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8008

# Run the application
CMD ["uvicorn", "healer.main:app", "--host", "0.0.0.0", "--port", "8008"]
