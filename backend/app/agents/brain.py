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

    async def recall_context(self, query: str = None, limit: int = 5) -> str:
        """
        Retrieves context using Vector Search (RAG) if available, falling back to recent files.
        """
        context = []
        
        # 1. Try Vector Search (Semantic)
        try:
            from app.core.rag import rag
            if query:
                logger.info(f"[BRAIN] Semantic searching for: '{query}'")
                rag_results = rag.query(query, n_results=limit)
                if rag_results:
                    context.append("--- Semantic Memory (RAG) ---")
                    context.extend(rag_results)
                    return "\n\n".join(context)
        except Exception as e:
            logger.warning(f"[BRAIN] RAG search failed: {e}")

        # 2. Fallback to Recent Files (Temporal)
        try:
            from app.core.storage import storage
            files = storage.list_files(limit=limit)
            for file_key in files:
                if file_key.endswith(".md"):
                    content = storage.get_file_content(file_key)
                    # Truncate content to avoid token overflow
                    summary = content[:1000] + "..." if len(content) > 1000 else content
                    context.append(f"--- Recent File: {file_key} ---\n{summary}\n")
            
            return "\n".join(context)
        except Exception as e:
            logger.error(f"[BRAIN] Error recalling context: {e}")
            return ""

    async def think(self, role: str, task_description: str, use_memory: bool = False) -> str:
        """
        Process a task description and return a plan or code.
        """
        logger.info(f"[BRAIN] {role} is thinking about: {task_description} (via Perplexity)")
        
        if use_memory:
            logger.info("[BRAIN] Accessing Long-Term Memory...")
            # Use the task description as the query for RAG
            memory_context = await self.recall_context(query=task_description)
            if memory_context:
                task_description = f"Context from Memory:\n{memory_context}\n\nTask: {task_description}"

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
            
            # Increase timeout and verify=True for production security
            async with httpx.AsyncClient(timeout=60.0) as client:
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
