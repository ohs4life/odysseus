"""FastAPI routes for the KB: query, stats, reindex.

All routes require the same auth as the rest of Odysseus (gated by the
app-level auth middleware). Endpoints are namespaced under /api/kb/.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.knowledgebase import config, indexer, meta, retriever  # noqa: E402

log = logging.getLogger("odysseus.routes.kb")

router = APIRouter(prefix="/api/kb", tags=["knowledgebase"])


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural-language question")
    top_k: int | None = Field(None, description="Override default top-K rerank count")


class CitationModel(BaseModel):
    id: int
    citation_id: str
    source_path: str
    title: str
    section: str
    page: str


class ChunkModel(BaseModel):
    chunk_id: str
    score: float
    citation: CitationModel
    text: str


class QueryResponse(BaseModel):
    query: str
    has_answer: bool
    confidence: float
    threshold: float
    chunks: list[ChunkModel]
    citations: list[CitationModel]
    prompt_block: str


@router.post("/query", response_model=QueryResponse)
def kb_query(req: QueryRequest) -> QueryResponse:
    """Run a hybrid retrieval over the KB.

    Returns the chunks that should be injected into the LLM prompt, plus a
    `has_answer` flag. The caller decides what to do with the result — usually
    inject `prompt_block` as a system context and force the LLM to cite.
    """
    config.init_dirs()
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")
    result = retriever.retrieve(req.query, top_k=req.top_k)
    return QueryResponse(
        query=result.query,
        has_answer=result.has_answer,
        confidence=result.confidence,
        threshold=result.threshold,
        chunks=[
            ChunkModel(
                chunk_id=c.chunk_id,
                score=c.score,
                citation=CitationModel(
                    id=i,
                    citation_id=c.chunk_id,
                    source_path=c.citation.get("source_path", ""),
                    title=c.citation.get("title", ""),
                    section=c.citation.get("section", ""),
                    page=c.citation.get("page", ""),
                ),
                text=c.text,
            )
            for i, c in enumerate(result.chunks, start=1)
        ],
        citations=[
            CitationModel(
                **c,
            )
            for c in result.as_citation_index()
        ],
        prompt_block=result.as_prompt_block(),
    )


@router.get("/stats")
def kb_stats() -> dict:
    """KB health summary: sources, chunks, index size, retrieval stats."""
    config.init_dirs()
    all_sources = meta.list_all_sources()
    by_status: dict[str, int] = {}
    total_chunks = 0
    total_bytes = 0
    for s in all_sources:
        by_status[s["status"]] = by_status.get(s["status"], 0) + 1
        total_chunks += s.get("chunk_count") or 0
        total_bytes += s.get("size_bytes") or 0
    try:
        col_count = indexer.get_chroma_collection().count()
    except Exception:
        col_count = None
    return {
        "kb_root": str(config.KB_ROOT),
        "source_roots": [str(p) for p in config.get("source_roots")],
        "sources": {"total": len(all_sources), "by_status": by_status},
        "chunks_db": total_chunks,
        "chroma_items": col_count,
        "bm25_index_exists": config.BM25_PATH.exists(),
        "embed_model": config.get("embed_model"),
        "rerank_model": config.get("rerank_model"),
        "confidence_threshold": config.get("confidence_threshold"),
        "settings": config.all(),
        "retrieval": meta.retrieval_stats(),
    }


@router.post("/reindex")
def kb_reindex() -> dict:
    """Re-scan source roots, parse new/changed files, and rebuild the index.

    Idempotent. Useful to call after dropping files into ~/knowledgebase/.
    """
    from src.knowledgebase import scanner
    config.init_dirs()
    scanner.full_ingest_pass()
    summary = indexer.index_parsed_sources()
    return {"ingest": "ok", "index": summary}
