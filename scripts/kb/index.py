#!/usr/bin/env python3
"""CLI: build the ChromaDB + bm25 indexes from parsed chunks.

Idempotent — only embeds chunks whose content hashes aren't already in the
vector store. Safe to run repeatedly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from src.knowledgebase import indexer  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build KB vector + keyword indexes.")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    summary = indexer.index_parsed_sources()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
