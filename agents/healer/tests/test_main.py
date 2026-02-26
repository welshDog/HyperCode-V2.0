import pytest
from fastapi.testclient import TestClient
from agents.healer.main import app

client = TestClient(app)

def test_service_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healer_online"

