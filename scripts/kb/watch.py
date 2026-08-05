#!/usr/bin/env python3
"""CLI: run the KB file watcher as a long-lived process.

Monitors all configured source roots (default: ~/knowledgebase/ and
data/knowledgebase/inbox/) and runs ingest+index whenever a supported file
appears or changes.

Run as:
    python -m scripts.kb.watch           # foreground, Ctrl-C to stop
    python -m scripts.kb.watch --once    # do one full scan and exit
"""

from __future__ import annotations

import argparse
import signal
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from src.knowledgebase import config, indexer, scanner, watcher  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Watch source roots and auto-ingest.")
    ap.add_argument("--once", action="store_true",
                    help="Run a single scan + index pass and exit (no watcher)")
    args = ap.parse_args(argv)

    config.init_dirs()

    if args.once:
        scanner.full_ingest_pass()
        summary = indexer.index_parsed_sources()
        print(summary)
        return 0

    observer, handler = watcher.start_watcher()

    def shutdown(*_a) -> None:
        handler.stop()
        observer.stop()
        observer.join()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"Watching {config.get('source_roots')} (Ctrl-C to stop)")
    try:
        # Initial pass in case files changed while we were down.
        scanner.full_ingest_pass()
        indexer.index_parsed_sources()
        handler.run_loop()
    except KeyboardInterrupt:
        shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
