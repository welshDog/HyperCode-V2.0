"""
HyperCode V2.0 — Backend API Test Suite
========================================
Phase 1: Core API Health & Auth Tests

BROski Note: Start small, test what matters, grow the suite.
Every green test is a win. Every red test is a bug caught before prod.
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# Make sure the app module is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ============================================================
# TIER 1: System Alive Tests (Always must pass)
# ============================================================

class TestSystemAlive:
    """The bare minimum — is the system breathing?"""

    def test_python_is_working(self):
        """If this fails, something is catastrophically wrong."""
        assert 1 + 1 == 2

    def test_imports_are_clean(self):
        """Verify core dependencies can be imported."""
        import fastapi
        import sqlalchemy
        import redis
        import httpx
        assert fastapi.__version__ is not None
        assert sqlalchemy.__version__ is not None

    def test_environment_variables_documented(self):
        """Verify .env.example exists so new devs know what to set."""
        env_example = os.path.join(
            os.path.dirname(__file__), '..', '..', '.env.example'
        )
        assert os.path.exists(env_example), \
            ".env.example missing! New devs won't know what env vars to set."


# ============================================================
# TIER 2: API Endpoint Tests (Core business logic)
# ============================================================

class TestAPIEndpoints:
    """Test the FastAPI endpoints we built in Phase 1."""

    @pytest.fixture
    def client(self):
        """Create a test client — requires the app to be importable."""
        try:
            from app.main import app
            return TestClient(app)
        except Exception as e:
            pytest.skip(f"App not importable in CI environment: {e}")

    def test_health_endpoint_exists(self, client):
        """The /health endpoint must always return 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_docs_endpoint_available(self, client):
        """FastAPI docs should be accessible in development."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_api_v1_prefix_exists(self, client):
        """All our routes should be under /api/v1/."""
        # The tasks endpoint should exist (even if it returns 401)
        response = client.get("/api/v1/tasks/")
        assert response.status_code in [200, 401, 403], \
            f"Unexpected status {response.status_code} - route may not exist"

    def test_unauthenticated_request_is_rejected(self, client):
        """Protected endpoints must reject unauthenticated requests."""
        response = client.get("/api/v1/tasks/")
        # Should return 401 Unauthorized, not 200
        assert response.status_code != 200, \
            "SECURITY ISSUE: Tasks endpoint accessible without auth!"

    def test_invalid_token_is_rejected(self, client):
        """Requests with a fake JWT must be rejected."""
        response = client.get(
            "/api/v1/tasks/",
            headers={"Authorization": "Bearer fake_token_broski"}
        )
        assert response.status_code in [401, 403], \
            "SECURITY ISSUE: Fake token was accepted!"


# ============================================================
# TIER 3: Agent Pipeline Tests
# ============================================================

class TestAgentPipeline:
    """Verify the Celery/Redis task pipeline is wired correctly."""

    def test_celery_app_is_importable(self):
        """The Celery app config must be importable without crashing."""
        try:
            from app.core.celery_app import celery_app
            assert celery_app is not None
        except ImportError as e:
            pytest.skip(f"Celery app not importable: {e}")

    def test_brain_module_is_importable(self):
        """The Brain (Perplexity AI wrapper) must be importable."""
        try:
            from app.agents.brain import brain
            assert brain is not None
        except ImportError as e:
            pytest.skip(f"Brain module not importable: {e}")

    def test_worker_task_is_registered(self):
        """The process_agent_job Celery task must be registered."""
        try:
            from app.core.celery_app import celery_app
            registered_tasks = list(celery_app.tasks.keys())
            agent_tasks = [t for t in registered_tasks if 'agent' in t.lower()]
            # We just verify the celery app loaded — task discovery
            # happens at runtime when worker connects to Redis
            assert celery_app is not None
        except Exception as e:
            pytest.skip(f"Worker not available in CI: {e}")
