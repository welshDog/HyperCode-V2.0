from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379"
    log_level: str = "INFO"
    
    # Agent Service URLs (Defaults based on docker-compose service names)
    agents: Dict[str, str] = {
        "project_strategist": "http://project-strategist:8001",
        "frontend_specialist": "http://frontend-specialist:8002",
        "backend_specialist": "http://backend-specialist:8003",
        "database_architect": "http://database-architect:8004",
        "qa_engineer": "http://qa-engineer:8005",
        "devops_engineer": "http://devops-engineer:8006",
        "security_engineer": "http://security-engineer:8007",
        "system_architect": "http://system-architect:8008",
        "coder_agent": "http://coder-agent:8002",
    }

    class Config:
        env_prefix = "ORCHESTRATOR_"

settings = Settings()
