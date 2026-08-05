"""Build the vector (ChromaDB) and keyword (bm25s) indexes from chunks.

Idempotent: only embeds chunks that aren't already in the vector index,
detected by content hash. Re-running on an unchanged KB is fast.

On startup, downloads the embedding + rerank models via fastembed's local
cache (~/.cache/fastembed or wherever the env points).
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

from . import config, meta

log = logging.getLogger("odysseus.kb.indexer")

# Lazy module-level singletons so we don't pay model-load cost on import.
_embedding_model = None
_chroma_client = None
_chroma_collection = None


def get_embedding_model():
    """Lazy-load the fastembed TextEmbedding model. Cached."""
    global _embedding_model
    if _embedding_model is None:
        from fastembed import TextEmbedding
        model_name = _get_embed_model_name()
        log.info("loading embedding model: %s", model_name)
        _embedding_model = TextEmbedding(model_name=model_name)
    return _embedding_model


# Lazy singletons for the rerank stack.
_rerank_tokenizer = None
_rerank_model = None
_rerank_torch = None


def get_rerank_model():
    """Lazy-load the cross-encoder reranker via transformers. Cached.

    fastembed 0.8 dropped TextCrossEncoder; we use transformers + AutoModel
    for SequenceClassification, which is what ms-marco cross-encoders are.
    """
    global _rerank_tokenizer, _rerank_model, _rerank_torch
    if _rerank_model is None:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        model_name = _get_rerank_model_name()
        log.info("loading rerank model: %s", model_name)
        _rerank_tokenizer = AutoTokenizer.from_pretrained(model_name)
        _rerank_model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _rerank_model.eval()
        _rerank_torch = torch
    return _rerank_model


def rerank_pairs(query: str, documents: list[str], *, batch_size: int = 32) -> list[float]:
    """Score (query, document) pairs. Returns one score per document.

    Scores are raw cross-encoder logits (typically in roughly [-10, +10]).
    Callers should normalize with sigmoid() before thresholding.
    """
    get_rerank_model()  # ensure loaded
    scores: list[float] = []
    with _rerank_torch.no_grad():
        for start in range(0, len(documents), batch_size):
            batch_docs = documents[start:start + batch_size]
            pairs = [(query, d) for d in batch_docs]
            features = _rerank_tokenizer(
                pairs, padding=True, truncation=True,
                max_length=512, return_tensors="pt",
            )
            logits = _rerank_model(**features).logits.squeeze(-1)
            scores.extend(float(x) for x in logits.tolist())
    return scores


def _get_embed_model_name() -> str:
    name = os.environ.get("ODYSSEUS_KB_EMBED_MODEL") or config.get("embed_model")
    return str(name)


def _get_rerank_model_name() -> str:
    name = os.environ.get("ODYSSEUS_KB_RERANK_MODEL") or config.get("rerank_model")
    return str(name)


def get_chroma_collection():
    """Return the ChromaDB collection for KB chunks. Creates if missing."""
    global _chroma_client, _chroma_collection
    if _chroma_collection is None:
        import chromadb
        config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_PATH))
        name = config.get("chroma_collection")
        _chroma_collection = _chroma_client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
    return _chroma_collection


def list_indexed_chunk_hashes() -> set[str]:
    """Return all content hashes currently in the ChromaDB collection."""
    col = get_chroma_collection()
    if col.count() == 0:
        return set()
    # `get()` returns ids + metadatas; we store content_hash in metadata.
    data = col.get(include=["metadatas"])
    return {m["content_hash"] for m in data["metadatas"] if m and m.get("content_hash")}


def _make_chunk_id(source_id: int, chunk_index: int) -> str:
    return f"s{source_id}-c{chunk_index}"


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns a list of float vectors."""
    model = get_embedding_model()
    # fastembed's embed yields numpy arrays; convert to plain lists.
    out = []
    for vec in model.embed(texts, batch_size=int(config.get("embed_batch_size"))):
        out.append([float(x) for x in vec])
    return out


def _build_chroma_from_cached_embeddings(
    rows: list[dict[str, Any]],
    embeddings_dir: Path,
) -> tuple[int, int]:
    """Read .npy files from disk and upsert to ChromaDB. Returns (indexed, sources_touched).

    No model loading or recomputation. Use this after `embed_parallel` writes
    the .npy files.
    """
    import numpy as np
    col = get_chroma_collection()
    BATCH = 500
    indexed = 0
    indexed_per_source: dict[int, int] = {}
    for start in range(0, len(rows), BATCH):
        batch = rows[start: start + BATCH]
        embeddings = []
        for r in batch:
            npy = embeddings_dir / f"s{r['source_id']}-c{r['chunk_index']}.npy"
            embeddings.append(np.load(npy).tolist())
        ids = [_make_chunk_id(r["source_id"], r["chunk_index"]) for r in batch]
        documents = [Path(r["chunk_path"]).read_text(encoding="utf-8") for r in batch]
        metadatas = [
            {
                "content_hash": r["content_hash"],
                "source_id": r["source_id"],
                "chunk_index": r["chunk_index"],
                "total_chunks": r["total_chunks"],
                "section": r["section"] or "",
                "source_rel_path": r["source_rel_path"],
                "source_parser": r["source_parser"] or "",
                "chunk_path": r["chunk_path"],
                "token_estimate": r["token_estimate"],
            }
            for r in batch
        ]
        col.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        indexed += len(batch)
        for r in batch:
            indexed_per_source[r["source_id"]] = indexed_per_source.get(r["source_id"], 0) + 1
    for source_id, count in indexed_per_source.items():
        meta.mark_embedded(source_id, count)
    return indexed, len(indexed_per_source)


def _embed_and_save_parallel(
    to_index: list[dict[str, Any]],
    embeddings_dir: Path,
) -> dict[str, int]:
    """Embed chunks in parallel, save to .npy, return counts.

    Falls back to serial embedding on ImportError (e.g. on systems without
    multiprocessing support).
    """
    from . import embed_parallel
    items: list[tuple[str, str]] = []
    for r in to_index:
        npy = embeddings_dir / f"s{r['source_id']}-c{r['chunk_index']}.npy"
        if not npy.exists():
            text = Path(r["chunk_path"]).read_text(encoding="utf-8")
            items.append((str(npy), text))
    if not items:
        return {"chunks_to_embed": 0, "chunks_embedded": 0, "workers": 0}
    workers = int(config.get("embed_parallel_workers"))
    started = time.time()
    done = embed_parallel.embed_parallel(items, workers=workers)
    return {
        "chunks_to_embed": len(items),
        "chunks_embedded": len(done),
        "workers": workers,
        "embed_seconds": round(time.time() - started, 1),
    }


def index_parsed_sources() -> dict[str, Any]:
    """Index every chunk from sources with status='parsed'. Returns counts."""
    config.init_dirs()
    chunks = meta.list_all_chunks()  # only joins sources where status='indexed'
    # Actually: we need 'parsed' status, not 'indexed'. Use raw query.
    conn = meta.get_conn()
    rows = conn.execute(
        """SELECT chunks.*, sources.absolute_path AS source_abs_path,
                  sources.source_root AS source_root, sources.rel_path AS source_rel_path,
                  sources.parser AS source_parser, sources.parsed_path AS source_parsed_path
           FROM chunks JOIN sources ON chunks.source_id = sources.id
           WHERE sources.status IN ('parsed', 'indexed')
           ORDER BY chunks.id ASC"""
    ).fetchall()
    rows = [dict(r) for r in rows]
    if not rows:
        return {"chunks_total": 0, "chunks_indexed": 0, "chunks_skipped": 0}

    existing_hashes = list_indexed_chunk_hashes()
    to_index = [r for r in rows if r["content_hash"] not in existing_hashes]
    if not to_index:
        # Already fully indexed; just make sure all 'parsed' are flipped to 'indexed'.
        _mark_all_indexed()
        return {"chunks_total": len(rows), "chunks_indexed": 0, "chunks_skipped": len(rows)}

    log.info("indexing %d new chunks (skipping %d already indexed)",
             len(to_index), len(rows) - len(to_index))

    # Two stages: (1) embed in parallel, save to .npy files;
    #             (2) load .npy files into ChromaDB.
    # Splitting them lets the user re-run the chroma stage without
    # re-embedding, and makes progress visible per-stage.
    embeddings_dir = config.INDEX_DIR / "embeddings"
    embeddings_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    embed_stats = _embed_and_save_parallel(to_index, embeddings_dir)
    log.info("embed stage: %s", embed_stats)

    indexed, sources_touched = _build_chroma_from_cached_embeddings(rows, embeddings_dir)
    log.info("chroma stage: %d items, %d sources", indexed, sources_touched)

    # Rebuild BM25 over the full chunk set (bm25s doesn't support incremental).
    _rebuild_bm25(rows)

    return {
        "chunks_total": len(rows),
        "chunks_indexed": len(to_index),
        "chunks_skipped": len(rows) - len(to_index),
        "embed": embed_stats,
        "duration_seconds": round(time.time() - t0, 2),
    }


def _mark_all_indexed() -> None:
    """Flip every 'parsed' source to 'indexed' with embedded_count = chunk_count."""
    conn = meta.get_conn()
    conn.execute(
        """UPDATE sources SET status='indexed', embedded_count=chunk_count,
                              embedded_at=?, updated_at=?
           WHERE status='parsed'""",
        (time.time(), time.time()),
    )


def _rebuild_bm25(all_chunks: list[dict[str, Any]]) -> None:
    """Rebuild the BM25 index from scratch. ~10k chunks/s; 100k ~ 10s."""
    import bm25s
    if not all_chunks:
        return
    log.info("building BM25 over %d chunks...", len(all_chunks))
    texts = [Path(r["chunk_path"]).read_text(encoding="utf-8") for r in all_chunks]
    # Keep references to metadata so we can resolve scores -> chunk records.
    corpus_tokens = bm25s.tokenize(texts, stopwords="en", show_progress=False)
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens, show_progress=False)
    config.BM25_PATH.parent.mkdir(parents=True, exist_ok=True)
    retriever.save(str(config.BM25_PATH), corpus=texts)
    log.info("BM25 saved to %s", config.BM25_PATH)


def load_bm25():
    """Load the persisted BM25 index. Returns None if no index yet."""
    if not config.BM25_PATH.exists():
        return None
    import bm25s
    try:
        retriever = bm25s.BM25.load(str(config.BM25_PATH), load_corpus=True)
    except Exception as e:
        log.warning("failed to load BM25 index: %s; rebuilding...", e)
        return None
    return retriever


def remove_source_from_index(source_id: int) -> None:
    """Drop all chunks of a source from the vector index."""
    col = get_chroma_collection()
    # Find chunk ids for this source.
    data = col.get(where={"source_id": source_id}, include=[])
    if data["ids"]:
        col.delete(ids=data["ids"])
