import asyncio
from typing import Dict, Any, List
import chromadb
from chromadb.config import Settings
import uuid
import os

class WeaverAgent:
    """
    WEAVER: The Pattern Intelligence
    Responsibility: Managing the Knowledge Graph and connecting ideas using ChromaDB.
    """
    def __init__(self, persist_path: str = "./data/chroma_db"):
        self.name = "WEAVER"
        self.role = "Knowledge Graph Manager"
        
        # Initialize ChromaDB Client
        # Check if running in Docker, might use HttpClient
        # For now, default to PersistentClient
        
        # Ensure directory exists
        os.makedirs(persist_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_path)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="nexus_knowledge",
            metadata={"hnsw:space": "cosine"} # Cosine similarity
        )
        print(f"[{self.name}] Initialized ChromaDB at {persist_path}")

    async def ingest_context(self, context_type: str, content: Any):
        """
        Ingests code, docs, or decisions into the knowledge graph (ChromaDB).
        """
        try:
            content_str = str(content)
            entry_id = str(uuid.uuid4())
            
            tags = self._extract_tags(content_str)
            metadata = {
                "type": context_type,
                "tags": ",".join(tags),
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
            # Add to ChromaDB
            self.collection.add(
                documents=[content_str],
                metadatas=[metadata],
                ids=[entry_id]
            )
            
            print(f"[{self.name}] Ingested {context_type}: {content_str[:50]}... (ID: {entry_id})")
            return {"status": "success", "id": entry_id}
            
        except Exception as e:
            print(f"[{self.name}] Error ingesting context: {e}")
            return {"status": "error", "message": str(e)}

    async def ingest_batch(self, contexts: List[Dict[str, Any]], rate_limit_delay: float = 0.1):
        """
        Ingests a batch of contexts with rate limiting and error handling.
        """
        results = []
        for ctx in contexts:
            context_type = ctx.get("type", "unknown")
            content = ctx.get("content", "")
            
            result = await self.ingest_context(context_type, content)
            results.append(result)
            
            # Rate limiting
            await asyncio.sleep(rate_limit_delay)
            
        return results


    async def retrieve_context(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves relevant context based on semantic similarity.
        """
        print(f"[{self.name}] Searching knowledge graph for: '{query}'")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                formatted_results.append({
                    "type": meta.get("type", "unknown"),
                    "content": doc,
                    "tags": meta.get("tags", "").split(","),
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
                
        return formatted_results

    def _extract_tags(self, content: str) -> List[str]:
        # Simple tag extractor for prototype
        tags = []
        text = content.lower()
        keywords = ["auth", "login", "refactor", "ui", "database", "test", "api", "docker"]
        for kw in keywords:
            if kw in text:
                tags.append(kw)
        return tags

async def test_weaver():
    # Use a temp path for testing
    weaver = WeaverAgent(persist_path="./data/chroma_test")
    
    # 1. Ingest some knowledge
    await weaver.ingest_context("doc", "Authentication System Architecture: Uses OAuth2 and JWT.")
    await weaver.ingest_context("code", "def login(user): # Legacy login function")
    await weaver.ingest_context("decision", "Refactor Decision: Move to async/await pattern for auth.")
    await weaver.ingest_context("ui", "Login Page: Uses React Hook Form and Zod validation.")

    # 2. Query
    results = await weaver.retrieve_context("refactor auth")
    print(f"\n[{weaver.name}] Found {len(results)} relevant items:")
    for res in results:
        print(f"- [{res['type']}] {res['content']} (Dist: {res['distance']:.4f})")

if __name__ == "__main__":
    asyncio.run(test_weaver())

