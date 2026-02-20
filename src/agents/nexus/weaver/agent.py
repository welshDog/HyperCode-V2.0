import asyncio
from typing import Dict, Any, List

class WeaverAgent:
    """
    WEAVER: The Pattern Intelligence
    Responsibility: Managing the Knowledge Graph and connecting ideas.
    """
    def __init__(self):
        self.name = "WEAVER"
        self.role = "Knowledge Graph Manager"
        self.memory_store = [] # Mock Vector DB

    async def ingest_context(self, context_type: str, content: Any):
        """
        Ingests code, docs, or decisions into the knowledge graph.
        """
        entry = {
            "type": context_type,
            "content": content,
            "tags": self._extract_tags(content)
        }
        self.memory_store.append(entry)
        print(f"[{self.name}] Ingested {context_type}: {str(content)[:50]}...")

    async def retrieve_context(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieves relevant context based on a query.
        """
        print(f"[{self.name}] Searching knowledge graph for: '{query}'")
        # Mock Semantic Search
        results = [m for m in self.memory_store if any(tag in query.lower() for tag in m["tags"])]
        return results

    def _extract_tags(self, content: Any) -> List[str]:
        # Simple tag extractor for prototype
        tags = []
        text = str(content).lower()
        keywords = ["auth", "login", "refactor", "ui", "database", "test"]
        for kw in keywords:
            if kw in text:
                tags.append(kw)
        return tags

async def test_weaver():
    weaver = WeaverAgent()
    
    # 1. Ingest some knowledge
    await weaver.ingest_context("doc", "Authentication System Architecture: Uses OAuth2 and JWT.")
    await weaver.ingest_context("code", "def login(user): # Legacy login function")
    await weaver.ingest_context("decision", "Refactor Decision: Move to async/await pattern for auth.")

    # 2. Query
    results = await weaver.retrieve_context("refactor auth")
    print(f"\n[{weaver.name}] Found {len(results)} relevant items:")
    for res in results:
        print(f"- [{res['type']}] {res['content']}")

if __name__ == "__main__":
    asyncio.run(test_weaver())
