# Use a lightweight Python base
FROM python:3.11-slim

WORKDIR /app

# Environment variables with defaults
ENV LLM_API_URL="http://host.docker.internal:8080/v1/chat/completions"
ENV MODEL_NAME="hf.co/Qwen/Qwen2.5-Coder-7B-Instruct"
ENV OPENAI_API_KEY=""

# Copy files
COPY SOUL.md .
COPY agent.py .

# Install dependencies
RUN pip install --no-cache-dir requests

# Run as non-root
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Start the agent
CMD ["python", "agent.py"]