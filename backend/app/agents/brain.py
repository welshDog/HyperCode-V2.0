import logging
from anthropic import AsyncAnthropic
from app.core.config import settings

logger = logging.getLogger(__name__)

class Brain:
    """
    The cognitive core of the HyperCode agent system.
    Currently powered by Anthropic Claude 3.5 Sonnet.
    """
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-latest" # Using latest Sonnet as requested

    async def think(self, role: str, task_description: str) -> str:
        """
        Process a task description and return a plan or code.
        """
        logger.info(f"[BRAIN] {role} is thinking about: {task_description}")
        
        try:
            response = await self.client.messages.create(
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": f"You are a {role}. Please provide a brief plan to execute this task: {task_description}"
                    }
                ],
                model=self.model,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"[BRAIN] Error thinking: {e}")
            return f"Error: {str(e)}"

# Global instance
brain = Brain()
