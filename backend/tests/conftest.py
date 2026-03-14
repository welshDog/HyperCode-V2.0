"""Pytest configuration and fixtures for HyperCode tests."""

import asyncio
import os
import pytest
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import redis.asyncio as redis

# Import your app modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.config import settings
from app.core.database import Base, get_db

# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db():
    """Create a new database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session):
    """Create test client with dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def redis_client():
    """Create Redis test client."""
    client = await redis.from_url(
        "redis://localhost:6379/1",
        decode_responses=True
    )
    yield client
    await client.close()


@pytest.fixture(scope="function")
def mock_anthropic_api_key(monkeypatch):
    """Mock Anthropic API key for tests."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-12345")


@pytest.fixture(scope="function")
def mock_openai_api_key(monkeypatch):
    """Mock OpenAI API key for tests."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-test-key-12345")


@pytest.fixture(scope="function")
async def authenticated_client(client, db):
    """Create authenticated test client."""
    # Create test user
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Get token
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    
    # Add auth header
    client.headers["Authorization"] = f"Bearer {token}"
    return client
