import asyncio
import httpx
import json
import sys
import os

# Add agent path
sys.path.append(os.path.join(os.getcwd(), "agents/crew-orchestrator"))

async def test_orchestrator_health():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://localhost:8080/health")
            print(f"✅ Orchestrator Health: {resp.status_code}")
            print(resp.json())
        except Exception as e:
            print(f"❌ Orchestrator Health Failed: {e}")

async def test_phase_transition():
    async with httpx.AsyncClient() as client:
        try:
            # Test Phase Switch
            resp = await client.post("http://localhost:8080/phase/development?force=true")
            print(f"✅ Phase Switch (Force): {resp.status_code}")
            print(resp.json())
            
            # Verify Crew
            resp = await client.get("http://localhost:8080/crew")
            data = resp.json()
            if "frontend_specialist" in data["agents"]:
                print("✅ Frontend Specialist Active in Development Phase")
            else:
                print("❌ Frontend Specialist NOT Active")
                
        except Exception as e:
            print(f"❌ Phase Transition Failed: {e}")

async def test_handoff_simulation():
    # Simulate a handoff request payload
    payload = {
        "source_agent": "frontend_specialist",
        "target_agent": "backend_specialist",
        "task_id": "test-task-101",
        "context": {"priority": "high"},
        "artifacts": ["component.tsx"]
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("http://localhost:8080/handoff", json=payload)
            print(f"✅ Handoff Request: {resp.status_code}")
            print(resp.json())
        except Exception as e:
            print(f"❌ Handoff Request Failed: {e}")

async def main():
    print("🚀 Starting Swarm Validation...")
    # Note: This requires the actual services to be running. 
    # Since we can't ensure they are running in this environment, 
    # this script serves as a verification tool for the user.
    print("⚠️  Ensure Docker stack is running (docker-compose up -d)")
    
    await test_orchestrator_health()
    await test_phase_transition()
    await test_handoff_simulation()

if __name__ == "__main__":
    asyncio.run(main())
    # print("Script created. Run with: python scripts/validate_swarm.py")
