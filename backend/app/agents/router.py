import logging
from app.agents.brain import brain
from app.agents.researcher import researcher
from app.agents.translator import translator
from app.agents.pulse import pulse

logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Routes tasks to the appropriate specialist agent based on task type or keywords.
    """
    def __init__(self):
        self.routes = {
            "research": researcher,
            "translate": translator,
            "health": pulse,
            "backend": brain # Fallback to generic Brain/Backend Specialist
        }

    async def route_task(self, task_type: str, payload: str, context: dict = None) -> str:
        """
        Routes the task to the correct agent.
        """
        agent = self.routes.get(task_type)
        
        # Simple keyword detection if task_type is generic
        if not agent or task_type == "general":
            lower_payload = payload.lower()
            if "research" in lower_payload or "find" in lower_payload:
                agent = researcher
                task_type = "research"
            elif "translate" in lower_payload or "explain" in lower_payload:
                agent = translator
                task_type = "translate"
            elif "health" in lower_payload or "metrics" in lower_payload:
                agent = pulse
                task_type = "health"
            else:
                # Default behavior
                logger.info(f"[Router] No specific agent found for '{task_type}', defaulting to Brain.")
                return await brain.think("Backend Specialist", payload)

        logger.info(f"[Router] Routing task to {agent.__class__.__name__}...")
        
        # Dispatch based on agent interface
        # Passing 'context' if the agent supports it (Duck Typing check or specific check)
        if agent == researcher:
            return await researcher.process(payload, context)
        elif agent == translator:
            return await translator.process(payload)
        elif agent == pulse:
            return await pulse.process(payload)
        else:
            return await brain.think("Backend Specialist", payload)

# Global instance
router = AgentRouter()
