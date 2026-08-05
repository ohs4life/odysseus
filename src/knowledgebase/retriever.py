"""Hybrid retrieval: BM25 + dense vectors -> RRF -> cross-encoder rerank.

This is the module the chat agent calls when it needs KB-grounded context.

Public API:
    retrieve(query, top_k=...) -> RetrievalResult
        .chunks         list of {text, citation, score, ...}
        .confidence     max rerank score, 0..1
        .has_answer     True iff confidence >= threshold

Anti-hallucination contract:
    The retriever itself does NOT generate text. It only returns the most
    relevant verbatim chunks plus a confidence score. The chat agent decides
    what to do with them (cite + answer vs "I don't know").
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import config, indexer, meta

log = logging.getLogger("odysseus.kb.retriever")


@dataclass
class Chunk:
    """A retrieved chunk, ready to be cited."""

    chunk_id: str
    text: str
    score: float                         # final rerank score, 0..1
    citation: dict[str, Any]             # {doc_slug, title, section, page, source_path}
    chunk_index: int
    source_id: int


@dataclass
class RetrievalResult:
    chunks: list[Chunk]
    confidence: float                    # max rerank score; 0..1
    has_answer: bool                     # confidence >= threshold
    threshold: float
    query: str

    def as_prompt_block(self, *, max_chars_per_chunk: int = 4000) -> str:
        """Render the chunks as a block to inject into the LLM prompt.

        Each chunk is wrapped with its citation id so the LLM can refer to it
        as [1], [2], etc. when answering.
        """
        if not self.has_answer or not self.chunks:
            return ""
        lines = ["<knowledge_base>"]
        for i, c in enumerate(self.chunks, start=1):
            cit = c.citation
            src = cit.get("source_path", "")
            title = cit.get("title", cit.get("doc_slug", ""))
            section = cit.get("section", "")
            page = cit.get("page", "")
            where = title + (f" — {section}" if section else "")
            if page:
                where += f" (page {page})"
            where += f" — {src}"
            text = c.text
            if len(text) > max_chars_per_chunk:
                text = text[: max_chars_per_chunk].rsplit(" ", 1)[0] + "…"
            lines.append(f"[{i}] {where}\n{text}")
        lines.append("</knowledge_base>")
        return "\n".join(lines)

    def as_citation_index(self) -> list[dict[str, Any]]:
        """Render a short citation list (for showing to the user after the answer)."""
        out = []
        for i, c in enumerate(self.chunks, start=1):
            cit = c.citation
            out.append({
                "id": i,
                "citation_id": c.chunk_id,
                "source_path": cit.get("source_path", ""),
                "title": cit.get("title", ""),
                "section": cit.get("section", ""),
                "page": cit.get("page", ""),
            })
        return out


_WORD_RE = re.compile(r"\w+")


def _tokenize_for_bm25(text: str) -> list[str]:
    """Lowercase word tokenization; bm25s can also do this but we need raw
    tokens for hybrid ranking parity."""
    return _WORD_RE.findall(text.lower())


def retrieve(query: str, *, top_k: int | None = None) -> RetrievalResult:
    """Run the full hybrid retrieval pipeline for a query.

    Returns chunks ordered by relevance (highest first). The caller should
    check `result.has_answer` and treat a False result as "no confident
    information in the KB for this query".
    """
    config.init_dirs()
    top_k = top_k or int(config.get("default_top_k"))
    rerank_top_k = int(config.get("rerank_top_k"))
    threshold = float(config.get("confidence_threshold"))

    # ---- Stage 1: dense retrieval (top-N) ----
    dense_hits = _dense_search(query, n=top_k * 3)
    # ---- Stage 2: keyword retrieval (top-N) ----
    bm25_hits = _bm25_search(query, n=top_k * 3)

    # ---- Stage 3: reciprocal rank fusion ----
    fused = _rrf_fuse(dense_hits, bm25_hits, k=int(config.RRF_K))
    # Trim to a manageable rerank budget.
    candidates = fused[: max(top_k, 30)]

    if not candidates:
        result = RetrievalResult(
            chunks=[], confidence=0.0, has_answer=False,
            threshold=threshold, query=query,
        )
        _audit_log(result, [])
        return result

    # ---- Stage 4: cross-encoder rerank ----
    reranked = _rerank(query, candidates, top_n=rerank_top_k)
    if not reranked:
        result = RetrievalResult(
            chunks=[], confidence=0.0, has_answer=False,
            threshold=threshold, query=query,
        )
        _audit_log(result, candidates)
        return result

    # Cross-encoder raw scores are unbounded (e.g. [-10, +10]); sigmoid -> [0,1].
    norm_scores = [_sigmoid(r["score"]) for r in reranked]
    chunks = [
        Chunk(
            chunk_id=r["chunk_id"],
            text=r["text"],
            score=norm,
            citation=r["citation"],
            chunk_index=r["chunk_index"],
            source_id=r["source_id"],
        )
        for r, norm in zip(reranked, norm_scores)
    ]
    confidence = max((c.score for c in chunks), default=0.0)
    has_answer = confidence >= threshold

    result = RetrievalResult(
        chunks=chunks, confidence=confidence,
        has_answer=has_answer, threshold=threshold, query=query,
    )
    _audit_log(result, candidates)
    return result


# -----------------------------------------------------------------------------
# Stage implementations
# -----------------------------------------------------------------------------


def _dense_search(query: str, *, n: int) -> list[dict[str, Any]]:
    col = indexer.get_chroma_collection()
    if col.count() == 0:
        return []
    model = indexer.get_embedding_model()
    qvec = list(model.embed([query]))[0]
    res = col.query(query_embeddings=[qvec], n_results=n)
    hits: list[dict[str, Any]] = []
    for rank, (cid, dist, meta_, doc) in enumerate(zip(
        res["ids"][0], res["distances"][0],
        res["metadatas"][0], res["documents"][0],
    )):
        # Chroma cosine distance in [0,2]; convert to similarity in [0,1].
        similarity = max(0.0, min(1.0, 1.0 - float(dist)))
        hits.append({
            "chunk_id": cid,
            "text": doc,
            "dense_score": similarity,
            "dense_rank": rank,
            "metadata": meta_,
        })
    return hits


def _bm25_search(query: str, *, n: int) -> list[dict[str, Any]]:
    bm25 = indexer.load_bm25()
    if bm25 is None:
        return []
    import bm25s
    q_tokens = bm25s.tokenize([query], stopwords="en", show_progress=False)
    # bm25s 0.3+ returns Results(documents, scores) where documents is an
    # array of {id, text} dicts (the corpus passed at index time).
    results = bm25.retrieve(q_tokens, k=n, show_progress=False)
    documents = results.documents[0]
    scores = results.scores[0]
    hits: list[dict[str, Any]] = []
    for rank, (doc, score) in enumerate(zip(documents, scores)):
        normalized = _sigmoid(float(score))
        bm25_id = int(doc["id"]) if isinstance(doc, dict) and "id" in doc else rank
        hits.append({
            "bm25_idx": bm25_id,
            "bm25_score": normalized,
            "bm25_rank": rank,
        })
    return hits


def _sigmoid(x: float) -> float:
    # Stable sigmoid.
    if x >= 0:
        z = pow(2.718281828, -x)
        return 1.0 / (1.0 + z)
    z = pow(2.718281828, x)
    return z / (1.0 + z)


def _rrf_fuse(
    dense_hits: list[dict[str, Any]],
    bm25_hits: list[dict[str, Any]],
    *,
    k: int,
) -> list[dict[str, Any]]:
    """Reciprocal Rank Fusion across the two ranked lists.

    Joins hits by chunk_id where possible. For bm25 hits, the chunk_id is
    resolved from the BM25 corpus ordering via metadata lookup.
    """
    fused: dict[str, dict[str, Any]] = {}

    for h in dense_hits:
        cid = h["chunk_id"]
        fused[cid] = {
            "chunk_id": cid,
            "text": h["text"],
            "metadata": h["metadata"],
            "rrf_score": 1.0 / (k + h["dense_rank"] + 1),
            "dense_score": h["dense_score"],
            "bm25_score": 0.0,
        }

    if bm25_hits:
        bm25_meta = _bm25_metadata_lookup()
        for h in bm25_hits:
            idx = h["bm25_idx"]
            meta_ = bm25_meta.get(idx)
            if not meta_:
                continue
            cid = meta_["chunk_id"]
            if cid in fused:
                fused[cid]["bm25_score"] = h["bm25_score"]
                fused[cid]["rrf_score"] += 1.0 / (k + h["bm25_rank"] + 1)
            else:
                # Need the actual text for reranking; read it lazily here.
                text = meta_.get("_text", "")
                fused[cid] = {
                    "chunk_id": cid,
                    "text": text,
                    "metadata": meta_,
                    "rrf_score": 1.0 / (k + h["bm25_rank"] + 1),
                    "dense_score": 0.0,
                    "bm25_score": h["bm25_score"],
                }
    return sorted(fused.values(), key=lambda x: x["rrf_score"], reverse=True)


def _bm25_metadata_lookup() -> dict[int, dict[str, Any]]:
    """Build an index: BM25 corpus position -> chunk metadata + text.

    This is the join key between bm25s (which returns {id, text} dicts into
    its in-memory corpus) and ChromaDB metadata (which has the real chunk ids).
    """
    # The BM25 corpus ids match the order of `texts` passed to index() in
    # indexer._rebuild_bm25, which is the order of all_chunks from
    # list_all_chunks(). So we just rebuild that ordering on demand.
    chunks = meta.list_all_chunks()
    lookup: dict[int, dict[str, Any]] = {}
    for i, c in enumerate(chunks):
        chunk_id = indexer._make_chunk_id(c["source_id"], c["chunk_index"])
        text = Path(c["chunk_path"]).read_text(encoding="utf-8")
        lookup[i] = {
            "chunk_id": chunk_id,
            "content_hash": c["content_hash"],
            "source_id": c["source_id"],
            "chunk_index": c["chunk_index"],
            "total_chunks": c["total_chunks"],
            "section": c.get("section") or "",
            "source_rel_path": c["source_rel_path"],
            "source_title": "",
            "source_parser": "",
            "chunk_path": c["chunk_path"],
            "token_estimate": c["token_estimate"],
            "_text": text,
        }
    return lookup


def _rerank(query: str, candidates: list[dict[str, Any]], *, top_n: int) -> list[dict[str, Any]]:
    if not candidates:
        return []
    texts = [c["text"] for c in candidates]
    raw_scores = indexer.rerank_pairs(query, texts)
    paired = []
    for cand, s in zip(candidates, raw_scores):
        paired.append({**cand, "score": float(s)})
    paired.sort(key=lambda x: x["score"], reverse=True)
    top = paired[:top_n]
    out: list[dict[str, Any]] = []
    for c in top:
        m = c.get("metadata", {}) or {}
        out.append({
            "chunk_id": c["chunk_id"],
            "text": c["text"],
            "score": c["score"],
            "source_id": int(m.get("source_id", 0)),
            "chunk_index": int(m.get("chunk_index", 0)),
            "citation": _build_citation(m),
        })
    return out


def _build_citation(metadata: dict[str, Any]) -> dict[str, Any]:
    """Build a clean citation dict from ChromaDB metadata."""
    rel = metadata.get("source_rel_path", "")
    title = metadata.get("source_title") or Path(rel).stem if rel else ""
    return {
        "doc_slug": Path(rel).stem if rel else "",
        "title": title,
        "section": metadata.get("section", ""),
        "page": metadata.get("page", ""),
        "source_path": rel,
        "chunk_path": metadata.get("chunk_path", ""),
    }


def _audit_log(result: RetrievalResult, candidates: list[dict[str, Any]]) -> None:
    """Record this retrieval so we can audit any past answer."""
    try:
        meta.log_retrieval(
            query=result.query,
            top_chunks=[
                {"chunk_id": c.chunk_id, "score": c.score}
                for c in result.chunks
            ] or [{"candidate_id": c.get("chunk_id"), "rrf": c.get("rrf_score")}
                  for c in candidates[:10]],
            confidence=result.confidence,
            answer_provided=result.has_answer,
        )
    except Exception:
        log.debug("failed to log retrieval", exc_info=True)
