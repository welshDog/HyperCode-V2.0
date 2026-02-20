import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.agents.nexus.cortex.agent import CortexAgent
from src.agents.nexus.bridge.agent import BridgeAgent
from src.agents.nexus.pulse.agent import PulseAgent
from src.agents.nexus.broski_stub import BroskiOrchestrator

async def run_full_flow():
    print("🚀 STARTING FULL NEXUS-PANTHEON SIMULATION\n" + "="*50)

    # 1. Initialize The Team
    cortex = CortexAgent()
    bridge = BridgeAgent()
    pulse = PulseAgent()
    broski = BroskiOrchestrator()

    # 2. User Input
    user_input = "Refactor the login function."
    print(f"\n👤 USER: '{user_input}'")

    # 3. Nexus Layer (Cognitive)
    intent = await cortex.analyze_intent(user_input)
    
    # 4. Handoff to Pantheon (Execution)
    print(f"\n🔄 Handoff: CORTEX -> BROski")
    orchestration_result = await broski.execute_task(intent)
    
    # 5. Result Translation (Bridge)
    print(f"\n🔄 Handoff: BROski -> BRIDGE")
    final_output = await bridge.translate_output(orchestration_result)
    
    print(f"\n🤖 BRIDGE to USER:\n{'-'*20}\n{final_output}\n{'-'*20}")

if __name__ == "__main__":
    asyncio.run(run_full_flow())
