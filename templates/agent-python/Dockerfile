
FROM python:3.11-alpine

# Create a non-root user
RUN adduser -D -u 1000 appuser

WORKDIR /app

# Install build deps minimally, then app deps
RUN apk add --no-cache libstdc++ \
    && pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN chown -R appuser:appuser /app
USER appuser

CMD ["python", "main.py"]
