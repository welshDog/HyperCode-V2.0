from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.rag import rag
from app.api import deps
from app.models import models

router = APIRouter()

class IngestRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20000)
    source: str = Field(min_length=1, max_length=200)
    metadata: Optional[dict] = None

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(default=5, ge=1, le=20)

@router.post("/ingest", response_model=dict)
def ingest_memory(
    request: IngestRequest,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Ingest text into the vector memory.
    """
    chunks_count = rag.ingest_document(request.content, request.source, request.metadata)
    if chunks_count == 0:
        raise HTTPException(status_code=500, detail="Failed to ingest document")
    return {"status": "success", "chunks_ingested": chunks_count}

@router.post("/query", response_model=dict)
def query_memory(
    request: QueryRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Semantic search in vector memory.
    """
    results = rag.query(request.query, request.limit)
    return {"results": results}

@router.post("/reset", response_model=dict)
def reset_memory(
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Wipe all memory.
    """
    rag.reset()
    return {"status": "memory_wiped"}
