import logging
from app.agents.brain import brain

logger = logging.getLogger(__name__)

class TranslatorAgent:
    """
    The Visualizer: Translates standard code into HyperCode's spatial, chunked logic.
    """
    def __init__(self):
        self.role = "Code Translator"
    
    async def process(self, code_snippet: str, target_paradigm: str = "HyperCode Spatial") -> str:
        """
        Translates code into a more accessible format.
        """
        logger.info(f"[{self.role}] Translating code to {target_paradigm}")
        
        prompt = (
            f"Act as a Cognitive Code Translator specializing in neurodiversity accessibility. "
            f"Take the following code snippet and refactor/explain it using {target_paradigm} principles. "
            f"This means: "
            f"- Break monolithic functions into small, single-responsibility chunks. "
            f"- Use descriptive, semantic variable names. "
            f"- Add spatial comments (ASCII art diagrams) to visualize data flow. "
            f"- Explain the 'Why' before the 'How'. "
            f"\n\nCode to translate:\n{code_snippet}"
        )
        
        return await brain.think(self.role, prompt)

# Global instance
translator = TranslatorAgent()
