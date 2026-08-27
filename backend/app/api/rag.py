"""
RAG API — ingest codebases, query indexed code, manage the retrieval pipeline.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.rag_engine import get_rag_pipeline

router = APIRouter(prefix="/api/rag", tags=["RAG"])


class IngestRequest(BaseModel):
    path: str  # Absolute path to codebase directory


class QueryRequest(BaseModel):
    query: str
    top_k: int = 10
    max_tokens: int = 6000


class ChunkOut(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    chunk_type: str
    name: Optional[str] = None
    score: float
    retrieval_method: str
    content_preview: str  # First 200 chars


@router.post("/ingest")
async def ingest_codebase(body: IngestRequest):
    """Ingest a codebase directory into the RAG pipeline."""
    import os
    if not os.path.isdir(body.path):
        raise HTTPException(status_code=400, detail=f"Directory not found: {body.path}")

    rag = get_rag_pipeline()
    rag.ingest(body.path)
    stats = rag.get_stats()
    return {
        "status": "indexed",
        "path": body.path,
        **stats,
    }


@router.post("/query")
async def query_codebase(body: QueryRequest):
    """Query the indexed codebase using hybrid retrieval + reranking."""
    rag = get_rag_pipeline()
    if not rag.indexed:
        raise HTTPException(
            status_code=400,
            detail="No codebase indexed. POST /api/rag/ingest first.",
        )

    results = rag.retrieve(body.query, top_k=body.top_k)
    return {
        "query": body.query,
        "total_results": len(results),
        "results": [
            ChunkOut(
                file_path=r.chunk.file_path,
                start_line=r.chunk.start_line,
                end_line=r.chunk.end_line,
                chunk_type=r.chunk.chunk_type,
                name=r.chunk.name,
                score=round(r.score, 4),
                retrieval_method=r.retrieval_method,
                content_preview=r.chunk.content[:200],
            )
            for r in results
        ],
    }


@router.post("/context")
async def build_context(body: QueryRequest):
    """Build assembled context string for LLM consumption."""
    rag = get_rag_pipeline()
    if not rag.indexed:
        raise HTTPException(
            status_code=400,
            detail="No codebase indexed. POST /api/rag/ingest first.",
        )

    context = rag.build_context(body.query, top_k=body.top_k, max_tokens=body.max_tokens)
    return {
        "query": body.query,
        "context_length": len(context),
        "context": context,
    }


@router.get("/stats")
async def get_rag_stats():
    """Get RAG pipeline indexing statistics."""
    rag = get_rag_pipeline()
    return rag.get_stats()
