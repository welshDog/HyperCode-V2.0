import logging
from app.agents.brain import brain

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    The Archivist: A specialized agent for deep technical research.
    Uses Perplexity to find cutting-edge information and format it for the Living Digital Paper.
    """
    def __init__(self):
        self.role = "Research Specialist"
    
    async def process(self, topic: str) -> str:
        """
        Conducts research on a given topic.
        """
        logger.info(f"[{self.role}] Starting research on: {topic}")
        
        prompt = (
            f"Act as an expert technical researcher and archivist. "
            f"Conduct a deep dive into the following topic: '{topic}'. "
            f"Focus on recent developments, best practices, and actionable insights. "
            f"Format the output as a structured technical summary with: "
            f"1. Executive Summary "
            f"2. Key Concepts & Definitions "
            f"3. Code Examples or Architectural Patterns "
            f"4. Pros & Cons "
            f"5. References or Further Reading. "
            f"Keep the tone professional, concise, and optimized for a neurodivergent audience (clear headers, bullet points, spatial logic)."
        )
        
        return await brain.think(self.role, prompt)

# Global instance
researcher = ResearchAgent()
