import json
from typing import Dict, Any

class BridgeAgent:
    """
    BRIDGE: The Output Translator
    Responsibility: Translating technical jargon into user-aligned language.
    """
    def __init__(self):
        self.name = "BRIDGE"
        self.role = "Translator"
        self.user_profile = {
            "technical_level": "expert", # novice, intermediate, expert
            "communication_style": "visual", # text, visual, metaphor
            "neurodivergent_traits": ["adhd", "pattern_matcher"]
        }

    async def translate_output(self, technical_output: Dict[str, Any]) -> str:
        """
        Translates raw system output into a format optimized for the user's cognitive profile.
        """
        print(f"[{self.name}] Translating output...")
        
        # Mock Translation Logic
        status = technical_output.get("status", "unknown")
        details = technical_output.get("details", {})
        
        if status == "success":
            return self._format_success(details)
        elif status == "error":
            return self._format_error(details)
        else:
            return f"System Status: {status}"

    def _format_success(self, details: Dict[str, Any]) -> str:
        if self.user_profile["communication_style"] == "visual":
            return f"✅ **SUCCESS**\n\n- **Action:** {details.get('action')}\n- **Result:** {details.get('result')}\n- **Next:** {details.get('next_steps')}"
        else:
            return f"Task completed successfully. {details.get('result')}"

    def _format_error(self, details: Dict[str, Any]) -> str:
        # ND-friendly error formatting (no wall of red text)
        return f"⚠️ **PAUSE**\n\nWe hit a snag: **{details.get('error_summary')}**.\n\nSuggested Fix:\n1. {details.get('fix_suggestion')}"

    async def set_user_profile(self, profile: Dict[str, Any]):
        self.user_profile.update(profile)
        print(f"[{self.name}] User profile updated: {self.user_profile}")
