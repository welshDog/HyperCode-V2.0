
import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from pathlib import Path
from typing import List, Dict, Any
from .config import ROOT_DIR, CODE_EXTENSIONS, DOC_EXTENSIONS

class EmbeddingEngine:
    def __init__(self, root_dir: Path = ROOT_DIR):
        self.root_dir = root_dir
        self.persist_dir = root_dir / ".ai" / "chroma_db"
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        # Use a lightweight, local embedding model
        # 'all-MiniLM-L6-v2' is a good balance of speed and quality
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="hypercode_context",
            embedding_function=self.ef
        )

    def index_files(self, file_paths: List[Path]):
        """Generate embeddings for a list of files."""
        ids = []
        documents = []
        metadatas = []
        
        for path in file_paths:
            try:
                # Relative path as ID
                rel_path = str(path.relative_to(self.root_dir))
                
                # Read content (truncate if too large)
                content = path.read_text(encoding="utf-8", errors="ignore")
                if not content.strip():
                    continue
                    
                # Simple truncation strategy: First 2000 chars + Last 1000 chars
                # This captures headers/imports and core logic often found at top/bottom
                if len(content) > 3000:
                    truncated_content = content[:2000] + "\n...[truncated]...\n" + content[-1000:]
                else:
                    truncated_content = content
                
                ids.append(rel_path)
                documents.append(truncated_content)
                metadatas.append({"path": rel_path, "type": path.suffix})
                
            except Exception as e:
                print(f"Failed to embed {path}: {e}")

        if ids:
            # Upsert (Update or Insert)
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Semantic search."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        output = []
        if results['ids']:
            for i, doc_id in enumerate(results['ids'][0]):
                output.append({
                    "id": doc_id,
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "snippet": results['documents'][0][i][:200] + "..." # Preview
                })
        return output

    def clear(self):
        """Reset the database."""
        self.client.delete_collection("hypercode_context")
        self.collection = self.client.create_collection(
            name="hypercode_context",
            embedding_function=self.ef
        )
