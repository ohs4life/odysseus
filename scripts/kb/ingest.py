#!/usr/bin/env python3
"""CLI: ingest a single file or directory into the KB.

Examples:
    # One-shot full ingest of all source roots:
    python -m scripts.kb.ingest

    # Ingest a single file:
    python -m scripts.kb.ingest /path/to/file.pdf

    # Ingest a directory recursively (registered as a custom source root):
    python -m scripts.kb.ingest /path/to/dir --as-root

    # Just scan (register, don't parse):
    python -m scripts.kb.ingest --scan-only

After parsing, run:
    python -m scripts.kb.index
to build the vector + keyword indexes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as a script from anywhere.
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from src.knowledgebase import config, scanner  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ingest files into the Odysseus KB.")
    ap.add_argument("path", nargs="?", help="File or directory to ingest (default: all configured source roots)")
    ap.add_argument("--as-root", action="store_true",
                    help="Treat <path> as an additional source root (persisted in config.json)")
    ap.add_argument("--scan-only", action="store_true",
                    help="Only register files in meta.sqlite; do not parse or chunk")
    ap.add_argument("--init", action="store_true",
                    help="Initialize KB directory structure and exit")
    args = ap.parse_args(argv)

    if args.init:
        config.init_dirs()
        print(f"Initialized KB at {config.KB_ROOT}")
        return 0

    config.init_dirs()
    roots = config.get("source_roots")

    # Optionally add a new source root.
    if args.path and args.as_root:
        new_root = Path(args.path).expanduser().resolve()
        if not new_root.exists():
            print(f"error: path does not exist: {new_root}", file=sys.stderr)
            return 2
        if new_root not in roots:
            roots = [*roots, new_root]
            _persist_source_roots(roots)
            print(f"Added source root: {new_root}")
        # No specific file to ingest in this mode; fall through to full scan.

    if args.scan_only:
        rows = scanner.scan_and_register(roots=roots)
        print(f"Registered {len(rows)} source file(s).")
        return 0

    # Always scan first so newly-discovered files are registered before
    # process_pending looks for them.
    scanner.scan_and_register(roots=roots)
    summary = scanner.process_pending(roots=roots)
    print(json.dumps(summary, indent=2))
    return 0


def _persist_source_roots(roots: list[Path]) -> None:
    """Persist a modified list of source roots in data/knowledgebase/config.json."""
    import json
    existing: dict = {}
    if config.CONFIG_PATH.exists():
        try:
            existing = json.loads(config.CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    existing["source_roots"] = [str(p) for p in roots]
    config.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.CONFIG_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    config.reset_for_tests()


if __name__ == "__main__":
    raise SystemExit(main())
