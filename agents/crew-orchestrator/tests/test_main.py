import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app

client = TestClient(app)

# Mock Redis to avoid needing a real instance for unit tests
@pytest.fixture
def mock_redis():
    with patch("main.redis_client", new=AsyncMock()) as mock:
        mock.ping.return_value = True
        mock.get.return_value = None
        mock.lrange.return_value = []
        yield mock

def test_health_check_no_redis():
    # If redis is None (default in test env if not connected), it should handle gracefully
    with patch("main.redis_client", None):
        response = client.get("/health")
        # Depending on implementation, it might return 503 or 200 with status info
        # Based on current code:
        # try: if redis_client: await redis_client.ping() ... return {"status": "healthy", ...}
        # except Exception as e: raise HTTPException(503)
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "redis": "connected"}

def test_list_agents():
    response = client.get("/agents")
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    # Check for known static agents
    agent_ids = [a["id"] for a in agents]
    assert "backend_specialist" in agent_ids
    assert "frontend_specialist" in agent_ids

@pytest.mark.asyncio
async def test_execute_task_simple(mock_redis):
    payload = {
        "task": {
            "id": "test-task-1",
            "type": "test",
            "description": "Simple test task",
            "agent": "backend-specialist",
            "requires_approval": False
        }
    }
    
    # We need to mock the httpx.AsyncClient call inside execute_task
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success", "output": "Task done"}
        
        response = client.post("/execute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "backend-specialist" in data["results"]

@pytest.mark.asyncio
async def test_execute_task_requires_approval(mock_redis):
    payload = {
        "task": {
            "id": "test-task-2",
            "type": "test",
            "description": "Risky task",
            "agent": "backend-specialist",
            "requires_approval": True
        }
    }
    
    # Mock Redis to return "approved" when polled
    # This is tricky because the code loops. We need side_effect to return None then Approved.
    mock_redis.get.side_effect = [
        None, # First check
        '{"status": "approved"}' # Second check
    ]
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "success"}
        
        with patch("asyncio.sleep", new_callable=AsyncMock): # Skip sleep
            response = client.post("/execute", json=payload)
            
            assert response.status_code == 200
            # Verify approval was published
            mock_redis.publish.assert_called()
