import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.agents.nexus.broski_stub import TesterAgent

class TwoKeyRuleVerifier:
    """
    Simulates the 'Two-Key' Rule:
    1. Key 1: Technical Validation (TESTER)
    2. Key 2: Cognitive Validation (BRIDGE - simulated here)
    """
    def __init__(self):
        self.tester = TesterAgent()
        
    async def verify_code_release(self, code_artifact: str, user_profile: str):
        print(f"🔒 Initiating Two-Key Verification for artifact: '{code_artifact}'")
        
        # Key 1: Technical Validation
        print("\n🔑 Key 1: TESTER Agent (Technical)")
        tech_result = await self.tester.verify_change({"artifact": code_artifact})
        
        if tech_result["status"] != "success":
            print("❌ Technical Validation FAILED. Release Blocked.")
            return False
            
        print("✅ Technical Validation PASSED.")
        
        # Key 2: Cognitive Validation (Simulated Bridge Logic)
        print("\n🔑 Key 2: BRIDGE Agent (Cognitive)")
        # Logic: Does this output match the user's need?
        # Mock Check: If user asked for 'Simple', is the code simple?
        is_cognitive_match = True 
        if "Complex" in code_artifact and "Simple" in user_profile:
             is_cognitive_match = False
             
        if not is_cognitive_match:
            print(f"❌ Cognitive Validation FAILED. Output too complex for user preference '{user_profile}'. Release Blocked.")
            return False
            
        print("✅ Cognitive Validation PASSED.")
        print("\n🚀 RELEASE AUTHORIZED.")
        return True

async def run_two_key_test():
    verifier = TwoKeyRuleVerifier()
    
    # Scenario 1: Good Release
    await verifier.verify_code_release("Simple React Component", "Simple Visual")
    
    # Scenario 2: Cognitive Mismatch
    print("\n" + "-"*30 + "\n")
    await verifier.verify_code_release("Complex Abstract Factory Pattern", "Simple Visual")

if __name__ == "__main__":
    asyncio.run(run_two_key_test())
