"""Knowledge base: ingest, index, retrieve.

Public surface:
    config         — paths and settings
    parsers        — file -> Markdown
    chunker        — Markdown -> chunks with YAML frontmatter
    meta           — SQLite index of sources
    scanner        — find new/changed files and ingest them
    indexer        — build ChromaDB + bm25 indexes from chunks
    embed_parallel — multiprocess embedding (fast on multi-core)
    retriever      — hybrid BM25 + dense + rerank with confidence
    grounding      — post-processor: enforce KB-grounded responses
    watcher        — FSEvents-based continuous ingestion
"""

from . import config, parsers, chunker, meta, scanner, indexer, embed_parallel, retriever, grounding, watcher  # noqa: F401
