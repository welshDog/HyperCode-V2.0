from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.rag import rag

router = APIRouter()

class IngestRequest(BaseModel):
    content: str
    source: str
    metadata: Optional[dict] = None

class QueryRequest(BaseModel):
    query: str
    limit: int = 5

@router.post("/ingest", response_model=dict)
def ingest_memory(request: IngestRequest) -> Any:
    """
    Ingest text into the vector memory.
    """
    chunks_count = rag.ingest_document(request.content, request.source, request.metadata)
    if chunks_count == 0:
        raise HTTPException(status_code=500, detail="Failed to ingest document")
    return {"status": "success", "chunks_ingested": chunks_count}

@router.post("/query", response_model=dict)
def query_memory(request: QueryRequest) -> Any:
    """
    Semantic search in vector memory.
    """
    results = rag.query(request.query, request.limit)
    return {"results": results}

@router.post("/reset", response_model=dict)
def reset_memory() -> Any:
    """
    Wipe all memory.
    """
    rag.reset()
    return {"status": "memory_wiped"}
