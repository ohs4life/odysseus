#!/usr/bin/env python3
"""CLI: print KB stats for a quick health check."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from src.knowledgebase import config, indexer, meta  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Print KB stats.")
    args = ap.parse_args(argv)

    config.init_dirs()
    all_sources = meta.list_all_sources()
    by_status: dict[str, int] = {}
    total_chunks = 0
    for s in all_sources:
        by_status[s["status"]] = by_status.get(s["status"], 0) + 1
        total_chunks += s.get("chunk_count") or 0

    retrieval = meta.retrieval_stats()

    try:
        col_count = indexer.get_chroma_collection().count()
    except Exception:
        col_count = None

    print(json.dumps({
        "kb_root": str(config.KB_ROOT),
        "source_roots": [str(p) for p in config.get("source_roots")],
        "sources": {
            "total": len(all_sources),
            "by_status": by_status,
        },
        "chunks_db": total_chunks,
        "chroma_items": col_count,
        "bm25_index_exists": config.BM25_PATH.exists(),
        "embed_model": config.get("embed_model"),
        "rerank_model": config.get("rerank_model"),
        "confidence_threshold": config.get("confidence_threshold"),
        "retrieval": retrieval,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
