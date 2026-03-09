from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "HyperCode Core"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Auth
    API_KEY: Optional[str] = None
    JWT_SECRET: str = "dev-secret-key"  # Changed Optional to str with default for dev
    HYPERCODE_JWT_SECRET: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database & Redis
    HYPERCODE_DB_URL: str = "postgresql://postgres:postgres@postgres:5432/hypercode"
    HYPERCODE_REDIS_URL: str = "redis://redis:6379/0"
    
    # AI
    ANTHROPIC_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    HYPERCODE_MEMORY_KEY: Optional[str] = None
    OLLAMA_HOST: str = "http://hypercode-ollama:11434"
    DEFAULT_LLM_MODEL: str = "mistral"
    PERPLEXITY_SESSION_AUTH: bool = False

    # Storage (MinIO/S3)
    MINIO_ENDPOINT: str = "http://minio:9000" # Internal Docker Hostname
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_REPORTS: str = "agent-reports"
    MINIO_SECURE: bool = False # False for local MinIO (http)
    
    # RAG (ChromaDB)
    CHROMA_HOST: str = "chroma"
    CHROMA_PORT: int = 8000
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2" # Fast, local model

    # Telemetry (OpenTelemetry)
    OTLP_ENDPOINT: str = "http://jaeger:4317"  # Default to Jaeger OTLP gRPC port
    OTLP_EXPORTER_DISABLED: bool = False
    SERVICE_NAME: str = "hypercode-core"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Allow extra fields in env
    )

settings = Settings()
