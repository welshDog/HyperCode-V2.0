# 🧠 The Brain (Cognitive Core)

The **Brain** is the intelligence engine of HyperCode, powered by **Perplexity AI (Sonar Pro)**. It enables agents to perform complex reasoning, research, and coding tasks.

## 1. Architecture

The Brain operates as an asynchronous service within the `hypercode-core` backend.

```mermaid
graph LR
    A[API / Task] --> B[Celery Worker]
    B --> C[Brain.think()]
    C --> D[Perplexity API]
    D --> C
    C --> B
    B --> E[Result / Database]
```

## 2. Configuration

The Brain requires a valid `PERPLEXITY_API_KEY` in the `.env` file.

```bash
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxx
```

### Models
Currently configured to use `sonar-pro` for maximum reasoning capability.

## 3. Usage

### Programmatic Access
You can invoke the Brain from any backend service or Celery task:

```python
from app.agents.brain import brain

async def solve_problem():
    result = await brain.think(
        role="Backend Specialist",
        task_description="Write a Python script to calculate Fibonacci."
    )
    print(result)
```

### Task API
You can also trigger the Brain via the REST API:

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Research Task",
    "description": "Find the latest trends in AI agents.",
    "priority": "high"
  }'
```

## 4. Swarm Integration

When a task is submitted, the **Crew Orchestrator** assigns it to a specialized agent (e.g., "Backend Specialist"). The agent then consults the **Brain** to generate a plan or solution.

### Verification
Check the Celery logs to see the Brain in action:

```powershell
docker logs -f celery-worker
```

Look for `[BRAIN] ... is thinking about:` messages.
