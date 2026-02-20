
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import sys
import logging

# Add project root to python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

try:
    from scripts.hafs.walker import ContextWalker
    from scripts.hafs.embeddings import EmbeddingEngine
except ImportError as e:
    print(f"Error importing HAFS: {e}")
    sys.exit(1)

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HAFS.API")

app = FastAPI(
    title="Hyper AI File System API",
    description="Agentic Interface for HAFS Context and Semantic Search",
    version="1.0.0"
)

# Initialize Engines
walker = ContextWalker()
embedding_engine = EmbeddingEngine(ROOT_DIR)

# --- Models ---

class ContextResponse(BaseModel):
    file: str
    metadata: Dict[str, Any]
    imports: List[str]
    imported_by: List[str]

class SuggestionResponse(BaseModel):
    file: str
    suggestions: List[str]

class SearchResult(BaseModel):
    id: str
    score: float
    snippet: str
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]

class ErrorContext(BaseModel):
    error_message: str
    stack_trace: Optional[str] = None
    file_path: Optional[str] = None

# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HAFS API"}

@app.get("/context", response_model=ContextResponse)
async def get_context(path: str = Query(..., description="File path relative to root")):
    """Get context metadata and dependencies for a file."""
    try:
        context = walker.get_context(path)
        if "error" in context:
            raise HTTPException(status_code=404, detail=context["error"])
        return context
    except Exception as e:
        logger.error(f"Context error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict", response_model=SuggestionResponse)
async def predict_next(path: str = Query(..., description="File path relative to root")):
    """Get predictive file suggestions."""
    try:
        suggestions = walker.predict_next(path)
        return {"file": path, "suggestions": suggestions}
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_model=SearchResponse)
async def semantic_search(
    query: str = Query(..., description="Semantic search query"),
    limit: int = Query(5, ge=1, le=20)
):
    """Perform semantic search on the codebase."""
    try:
        results = embedding_engine.search(query, n_results=limit)
        formatted = []
        for r in results:
            formatted.append({
                "id": r["id"],
                "score": r["distance"] if r["distance"] is not None else 0.0,
                "snippet": r["snippet"],
                "metadata": r["metadata"]
            })
        return {"query": query, "results": formatted}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/diagnose", response_model=SearchResponse)
async def diagnose_error(error: ErrorContext):
    """
    Self-Correction Endpoint:
    Diagnose an error by searching for relevant code and similar error patterns.
    """
    try:
        # Construct a search query from the error
        query = f"Error: {error.error_message}"
        if error.file_path:
            query += f" in {error.file_path}"
        
        # Search for code relevant to the error
        results = embedding_engine.search(query, n_results=5)
        
        formatted = []
        for r in results:
            formatted.append({
                "id": r["id"],
                "score": r["distance"] if r["distance"] is not None else 0.0,
                "snippet": r["snippet"],
                "metadata": r["metadata"]
            })
        return {"query": query, "results": formatted}
    except Exception as e:
        logger.error(f"Diagnosis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
