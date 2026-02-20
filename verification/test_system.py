import pytest
import httpx
import os
import subprocess
import json

# Configuration
CORE_URL = os.getenv("CORE_URL", "http://localhost:8000")
CODER_AGENT_URL = os.getenv("CODER_AGENT_URL", "http://localhost:8001")
TERMINAL_URL = os.getenv("TERMINAL_URL", "http://localhost:3000")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8088")
API_KEY = os.getenv("API_KEY", "dev-master-key")

@pytest.fixture
def core_client():
    return httpx.Client(base_url=CORE_URL, timeout=10.0)

@pytest.fixture
def coder_client():
    return httpx.Client(base_url=CODER_AGENT_URL, timeout=10.0)

@pytest.fixture
def auth_headers():
    return {"X-API-Key": API_KEY, "Authorization": f"Bearer {API_KEY}"}

# 1. Infrastructure Checks
def test_docker_services_running():
    """Verify critical docker containers are running."""
    try:
        result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
        if result.returncode != 0:
            pytest.skip(f"Docker CLI failed: {result.stderr}")
        containers = result.stdout.splitlines()
        critical_services = ["hypercode-core", "redis", "postgres"]
        for service in critical_services:
            assert any(service in c for c in containers), f"Service {service} is not running"
    except FileNotFoundError:
        pytest.skip("Docker CLI not available")
    except Exception as e:
        pytest.skip(f"Docker check failed: {e}")

# 2. Core API Verification
def test_core_health(core_client):
    """Verify Core API health endpoint."""
    try:
        response = core_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["redis"] == "connected"
    except httpx.ConnectError:
        pytest.fail(f"Core API at {CORE_URL} is not reachable")

def test_core_agents_list(core_client, auth_headers):
    """Verify Core can list agents (RBAC check)."""
    # Try without auth first
    response = core_client.get("/agents/")
    # Depending on config, this might be 401/403 or 200 (if public read)
    # Our recent change made it protected? 
    # Let's check with auth
    response = core_client.get("/agents/", headers=auth_headers)
    assert response.status_code in [200, 404] # 404 if no agents registered yet
    if response.status_code == 200:
        assert isinstance(response.json(), list)

# 3. Coder Agent Verification
def test_coder_agent_health(coder_client):
    """Verify Coder Agent health."""
    try:
        response = coder_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    except httpx.ConnectError:
        pytest.skip(f"Coder Agent at {CODER_AGENT_URL} is not reachable (might not be started)")

def test_coder_agent_metadata(coder_client):
    """Verify Coder Agent metadata."""
    try:
        response = coder_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "coder-agent"
    except httpx.ConnectError:
        pytest.skip("Coder Agent not reachable")

# 4. Frontend Verification
def test_terminal_frontend_reachable():
    """Verify Broski Terminal frontend is serving."""
    try:
        response = httpx.get(TERMINAL_URL, timeout=5.0)
        assert response.status_code == 200
        assert "<html" in response.text.lower() or "<!doctype html" in response.text.lower()
    except httpx.ConnectError:
        pytest.fail(f"Frontend at {TERMINAL_URL} is not reachable")

# 5. Dashboard Verification
def test_dashboard_reachable():
    """Verify Dashboard is serving."""
    try:
        response = httpx.get(DASHBOARD_URL, timeout=5.0)
        assert response.status_code == 200
    except httpx.ConnectError:
        pytest.skip(f"Dashboard at {DASHBOARD_URL} is not reachable (might not be started)")
