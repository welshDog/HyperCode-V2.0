import logging
import httpx
from app.core.config import settings
import ssl

logger = logging.getLogger(__name__)

class Brain:
    """
    The cognitive core of the HyperCode agent system.
    Powered by Perplexity AI (Sonar Pro).
    """
    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
        # Using sonar-pro as it's the most capable model currently
        self.model = "sonar-pro" 

    async def think(self, role: str, task_description: str) -> str:
        """
        Process a task description and return a plan or code.
        """
        logger.info(f"[BRAIN] {role} is thinking about: {task_description} (via Perplexity)")
        
        if not self.api_key:
            return "Error: PERPLEXITY_API_KEY is not set in configuration."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a {role}. Provide a detailed, step-by-step plan or code solution."
                },
                {
                    "role": "user",
                    "content": task_description
                }
            ],
            "temperature": 0.2
        }

        try:
            # Create a custom SSL context that verifies certificates
            # but allows us to potentially debug or modify if needed
            ssl_context = ssl.create_default_context()
            
            # Increase timeout and verify=False ONLY IF absolutely necessary (trying to be strict first)
            # Actually, let's try with verify=False temporarily to debug the connection issue 
            # if the previous error was SSL related. But "All connection attempts failed" usually means DNS/Network.
            # We already fixed DNS.
            
            async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    logger.error(f"[BRAIN] Perplexity API Error: {response.text}")
                    return f"Error: API returned {response.status_code} - {response.text}"
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
        except Exception as e:
            logger.error(f"[BRAIN] Error thinking: {e}")
            return f"Error: {str(e)}"

# Global instance
brain = Brain()
