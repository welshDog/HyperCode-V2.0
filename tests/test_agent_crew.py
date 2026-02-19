"""
Test suite for HyperCode Agent Crew
"""
import pytest
import httpx
import asyncio
import json

ORCHESTRATOR_URL = "http://localhost:8080"

@pytest.mark.asyncio
async def test_orchestrator_health():
    """Test orchestrator health endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORCHESTRATOR_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_agents_status():
    """Test that all agents are reachable"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORCHESTRATOR_URL}/agents/status")
        assert response.status_code == 200
        agents = response.json()
        
        # Should have all 8 agents
        assert len(agents) == 8
        
        # Check critical agents are online
        agent_names = [a["agent"] for a in agents]
        assert "project_strategist" in str(agent_names)
        assert "frontend_specialist" in str(agent_names)

@pytest.mark.asyncio
async def test_plan_feature():
    """Test planning a feature"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{ORCHESTRATOR_URL}/plan",
            json={
                "task": "Create a simple login form",
                "context": {"tech_stack": "React"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "planning"

@pytest.mark.asyncio
async def test_workflow_creation():
    """Test starting a workflow"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ORCHESTRATOR_URL}/workflow/feature",
            json={
                "workflow_type": "feature",
                "description": "User authentication",
                "requirements": {"auth_type": "JWT"}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "workflow_id" in data
        assert data["type"] == "feature"

@pytest.mark.asyncio
async def test_agent_direct_execution():
    """Test direct agent execution"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{ORCHESTRATOR_URL}/agent/frontend_specialist/execute",
            json={
                "agent": "frontend_specialist",
                "message": "Create a button component",
                "context": {}
            }
        )
        # May fail if agent is busy, but should not return 404
        assert response.status_code in [200, 503]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
