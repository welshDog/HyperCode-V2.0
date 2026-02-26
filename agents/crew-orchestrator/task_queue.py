from arq import create_pool
from arq.connections import RedisSettings
from arq.worker import run_worker
import asyncio
import httpx
import json
import logging

logger = logging.getLogger(__name__)

# Task definitions
async def execute_agent_task(ctx, agent_name: str, task: dict):
    """Worker function that executes agent tasks"""
    logger.info(f"Executing task {task.get('id')} on {agent_name}")
    
    agent_url = f"http://{agent_name}:8000" if ":" not in agent_name else agent_name
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(f"{agent_url}/execute", json=task)
            response.raise_for_status()
            result = response.json()
        
        # Store result in Redis
        task_id = task.get('id', 'unknown')
        await ctx['redis'].set(
            f"task_result:{task_id}", 
            json.dumps(result),
            ex=3600 * 24  # Expire after 24 hours
        )
        
        return result
    except Exception as e:
        logger.error(f"Task {task.get('id')} failed: {e}")
        # Could implement retry logic here or let ARQ handle it via retry_jobs
        raise

# Worker settings
class WorkerSettings:
    redis_settings = RedisSettings(host='redis', port=6379)
    functions = [execute_agent_task]
    max_jobs = 10
    job_timeout = 600  # 10 minutes
    allow_abort_jobs = True

async def get_redis_pool():
    return await create_pool(WorkerSettings.redis_settings)
