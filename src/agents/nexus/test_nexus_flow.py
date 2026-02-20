import asyncio
import sys
import os

# Add src to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.agents.nexus.cortex.agent import CortexAgent
from src.agents.nexus.bridge.agent import BridgeAgent
from src.agents.nexus.pulse.agent import PulseAgent

async def run_nexus_simulation():
    print("🚀 STARTING NEXUS COGNITIVE LAYER SIMULATION\n" + "="*50)

    # 1. Initialize Agents
    cortex = CortexAgent()
    bridge = BridgeAgent()
    pulse = PulseAgent()

    # 2. Simulate User Input (Intent Understanding)
    user_input = "I need to refactor the auth_service.py to be more readable."
    print(f"\n👤 USER: '{user_input}'")

    # 3. PULSE Check (Energy Level)
    await pulse.monitor_activity("keystroke", None) # Simulate active typing
    energy_status = await pulse.get_energy_report()
    print(f"\n[{pulse.name}] Energy Check: {energy_status}")

    if energy_status['energy_level'] > 50:
        # 4. CORTEX Analysis
        intent = await cortex.analyze_intent(user_input)
        
        # 5. CORTEX -> BROski Handoff (Simulated)
        handoff = await cortex.handoff_to_orchestrator(intent)

        # 6. Simulate Technical Execution Result (Mock from BROski)
        technical_result = {
            "status": "success",
            "details": {
                "action": "Refactored auth_service.py",
                "result": "Reduced complexity by 40%. Added docstrings.",
                "next_steps": "Review PR #123"
            }
        }

        # 7. BRIDGE Translation
        print(f"\n[{bridge.name}] Translating Technical Result...")
        user_message = await bridge.translate_output(technical_result)
        print(f"\n🤖 BRIDGE to USER:\n{'-'*20}\n{user_message}\n{'-'*20}")
    
    else:
        print(f"\n[{pulse.name}] 🛑 User energy too low. Suggesting break instead of complex task.")

if __name__ == "__main__":
    asyncio.run(run_nexus_simulation())
