# HyperCode Approved Patterns

## FastAPI agent service template

```python
from fastapi import FastAPI
import redis
import os

app = FastAPI()
r = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=6379)

@app.on_event('startup')
async def startup():
    r.publish('hypercode:system', '{"event": "started", "agent": "MY_AGENT"}')

@app.get('/health')
async def health():
    return {"status": "healthy", "agent": "MY_AGENT"}
```

## Config pattern — ENV ONLY

```python
# GOOD
ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')

# BAD — never hardcode
ANTHROPIC_KEY = 'sk-ant-...'
```

## Structured logging

```python
import structlog
log = structlog.get_logger()
log.info('agent_started', name='my-agent', port=8080)
```
