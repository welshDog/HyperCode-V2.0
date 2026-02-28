import logging
from app.agents.brain import brain

logger = logging.getLogger(__name__)

class PulseAgent:
    """
    The Medic: Interprets system health metrics into plain English.
    """
    def __init__(self):
        self.role = "System Medic"
    
    async def process(self, health_data: dict) -> str:
        """
        Analyzes health data and provides a human-readable diagnosis.
        """
        logger.info(f"[{self.role}] Analyzing system pulse...")
        
        data_str = str(health_data)
        
        prompt = (
            f"Act as a friendly, expert DevOps Medic. "
            f"Analyze the following system health metrics and provide a 'Patient Diagnosis'. "
            f"Do not just list numbers. Explain what they mean in plain English. "
            f"If everything is good, say so with enthusiasm. "
            f"If there are issues, prioritize them by severity and suggest a fix. "
            f"Keep it conversational (like a helpful BROski). "
            f"\n\nMetrics:\n{data_str}"
        )
        
        return await brain.think(self.role, prompt)

# Global instance
pulse = PulseAgent()
