"""File-system watcher: react to new/changed files in source roots in real time.

Uses watchdog (FSEvents on macOS, inotify on Linux). When a supported file
appears or changes, run it through the scanner + processor pipeline. When
a file is deleted, mark its chunks for re-indexing (the actual cleanup
happens on the next index pass).

This is the "I will be adding more" requirement made concrete: drop a PDF
in ~/knowledgebase/seminars/, and within a second it's in the KB.
"""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Any

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from . import config, scanner

log = logging.getLogger("odysseus.kb.watcher")


class _KBEventHandler(FileSystemEventHandler):
    """Translate raw FS events into ingestion calls. Debounced to coalesce
    editors that do many writes in quick succession (vim, Pages, etc.)."""

    def __init__(self) -> None:
        super().__init__()
        self._pending: dict[str, float] = {}
        self._lock = threading.Lock()
        self._stopped = threading.Event()
        # Debounce: 1.5s after the last write, run ingest. Tuned for typical
        # editor save patterns; can be raised if needed.
        self._debounce_seconds = 1.5

    def _schedule(self, path: str) -> None:
        with self._lock:
            self._pending[path] = time.time()

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._schedule(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._schedule(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        # Treat moves as create + delete.
        if not event.is_directory:
            self._schedule(event.dest_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            # Mark the file as gone; scanner.process_pending won't see it,
            # so we record deletion in meta for cleanup.
            try:
                from . import meta
                abs_path = Path(event.src_path).resolve()
                # Best-effort: mark matching rows as 'deleted' if path matches.
                # The next index pass will purge them.
                conn = meta.get_conn()
                conn.execute(
                    "UPDATE sources SET status='deleted', updated_at=? WHERE absolute_path=?",
                    (time.time(), str(abs_path)),
                )
            except Exception:
                log.debug("deletion bookkeeping failed", exc_info=True)

    def run_loop(self) -> None:
        """Block, draining the debounce queue."""
        while not self._stopped.is_set():
            time.sleep(0.5)
            now = time.time()
            ready: list[str] = []
            with self._lock:
                for path, ts in list(self._pending.items()):
                    if now - ts >= self._debounce_seconds:
                        ready.append(path)
                        del self._pending[path]
            for path in ready:
                self._ingest_path(path)

    def _ingest_path(self, path: str) -> None:
        p = Path(path)
        if not p.exists():
            return
        # Find which source root this path belongs to.
        for root in config.get("source_roots"):
            try:
                p.resolve().relative_to(Path(root).resolve())
                break
            except ValueError:
                continue
        else:
            return
        # Check it's a supported file type.
        if p.name in config.SKIP_FILENAMES:
            return
        if p.name.startswith(config.SKIP_PREFIXES):
            return
        if p.suffix.lower() not in config.SUPPORTED_EXTS:
            return
        try:
            scanner.scan_and_register()
            scanner.process_pending()
        except Exception:
            log.exception("watcher ingest failed for %s", path)

    def stop(self) -> None:
        self._stopped.set()


def start_watcher(*, daemon: bool = True) -> tuple[Observer, _KBEventHandler]:
    """Start the watcher. Returns (observer, handler). Call handler.run_loop()
    in a thread, and observer.stop() + observer.join() to shut down."""
    config.init_dirs()
    handler = _KBEventHandler()
    observer = Observer()
    for root in config.get("source_roots"):
        rp = Path(root)
        if not rp.exists():
            log.info("watcher: source root %s does not exist; skipping", rp)
            continue
        observer.schedule(handler, str(rp), recursive=True)
        log.info("watcher: monitoring %s", rp)
    observer.daemon = daemon
    observer.start()
    return observer, handler


def watch_forever() -> None:
    """Convenience entrypoint: blocks until KeyboardInterrupt."""
    observer, handler = start_watcher()
    try:
        handler.run_loop()
    except KeyboardInterrupt:
        pass
    finally:
        handler.stop()
        observer.stop()
        observer.join()
