#!/usr/bin/env python3
"""CLI: run a single query against the KB and print the result.

Useful for smoke-testing retrieval quality without going through the chat UI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from src.knowledgebase import config, retriever  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Query the KB.")
    ap.add_argument("query", help="Query text")
    ap.add_argument("--top-k", type=int, default=None)
    ap.add_argument("--show-block", action="store_true",
                    help="Print the prompt block (what would be injected into the LLM)")
    args = ap.parse_args(argv)

    config.init_dirs()
    result = retriever.retrieve(args.query, top_k=args.top_k)

    out = {
        "query": result.query,
        "confidence": result.confidence,
        "threshold": result.threshold,
        "has_answer": result.has_answer,
        "chunks": [
            {
                "chunk_id": c.chunk_id,
                "score": c.score,
                "citation": c.citation,
                "preview": c.text[:200] + ("…" if len(c.text) > 200 else ""),
            }
            for c in result.chunks
        ],
        "citations": result.as_citation_index(),
    }
    print(json.dumps(out, indent=2))
    if args.show_block:
        print("\n--- prompt block ---")
        print(result.as_prompt_block() or "(no confident answer; would inject 'no confident results' message)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
