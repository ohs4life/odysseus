"""Find new/changed files in source roots and run them through the ingest
pipeline (parse -> chunk -> write chunks to disk -> mark 'parsed' in meta).

Idempotent: re-running on an unchanged KB is a no-op. Re-running on a changed
file re-parses and re-chunks it (the indexer will pick up the new chunks
separately).
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, Iterable

from . import config, hash as hashlib
from . import chunker, meta, parsers

log = logging.getLogger("odysseus.kb.scanner")


def _is_skipped(path: Path) -> bool:
    if path.name in config.SKIP_FILENAMES:
        return True
    if path.name.startswith(config.SKIP_PREFIXES):
        return True
    if path.suffix.lower() not in config.SUPPORTED_EXTS:
        return True
    return False


def iter_source_files(roots: Iterable[Path] | None = None) -> Iterable[tuple[Path, Path, Path]]:
    """Yield (source_root, rel_path, absolute_path) for every supported file.

    Skips hidden files, .DS_Store, unsupported extensions. Yields files in
    deterministic order so repeated scans are predictable.
    """
    roots = list(roots) if roots is not None else config.get("source_roots")
    for root in roots:
        if not root.exists():
            log.debug("source root does not exist, skipping: %s", root)
            continue
        root = root.resolve()
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if _is_skipped(path):
                continue
            rel = path.relative_to(root)
            yield (root, rel, path)


def scan_and_register(*, roots: Iterable[Path] | None = None) -> list[dict[str, Any]]:
    """Register all source files in meta.sqlite. Does NOT parse yet.

    Returns the list of source records that need parsing (status='pending'
    or 'error', or content_hash changed since last scan). Use
    `process_pending()` to actually parse them.
    """
    rows = []
    for source_root, rel_path, abs_path in iter_source_files(roots):
        try:
            st = abs_path.stat()
        except FileNotFoundError:
            # File disappeared between rglob and stat. Skip silently.
            continue
        content_hash = hashlib.sha256_file(abs_path)
        source_id = meta.upsert_source(
            source_root=source_root,
            rel_path=rel_path,
            absolute_path=abs_path,
            content_hash=content_hash,
            size_bytes=st.st_size,
            mtime=st.st_mtime,
        )
        rows.append(meta.get_source(source_id))
    return rows


def process_pending(*, limit: int = 50, roots: Iterable[Path] | None = None) -> dict[str, int]:
    """Find pending sources and parse + chunk them.

    Returns counts: {"scanned": N, "parsed": P, "failed": F, "skipped": S}.
    """
    config.init_dirs()
    pending = meta.list_pending_sources(limit=10_000)
    # Filter to pending only (list_pending_sources already does that).
    counts = {"scanned": len(pending), "parsed": 0, "failed": 0, "skipped": 0}

    for src in pending:
        # Only process sources in our configured roots (in case meta has stale rows).
        if roots is not None:
            root = Path(src["source_root"]).resolve()
            if not any(root == Path(r).resolve() for r in roots):
                counts["skipped"] += 1
                continue
        try:
            _process_one(src)
            counts["parsed"] += 1
        except Exception as e:
            log.exception("failed to process source %s", src["absolute_path"])
            meta.update_source_status(
                src["id"], status="error", error=f"{type(e).__name__}: {e}"
            )
            counts["failed"] += 1
    return counts


def _process_one(src: dict[str, Any]) -> None:
    """Parse + chunk one source file. Updates meta.sqlite + writes chunks."""
    abs_path = Path(src["absolute_path"])
    source_root = Path(src["source_root"])
    rel_path = Path(src["rel_path"])
    source_id = int(src["id"])

    slug = parsers.doc_slug(rel_path)
    parsed_dir = config.PARSED_DIR / slug
    chunk_dir = config.CHUNKS_DIR / slug
    parsed_dir.mkdir(parents=True, exist_ok=True)
    chunk_dir.mkdir(parents=True, exist_ok=True)

    # Wipe any prior chunks for this source before re-emitting — chunks are
    # derived state and always replaced together when the source is reprocessed.
    if chunk_dir.exists():
        for old in chunk_dir.glob("chunk-*.md"):
            old.unlink()

    md_text, parser_meta = parsers.parse(abs_path)
    parsed_path = parsed_dir / f"{slug}.md"
    parsed_path.write_text(md_text, encoding="utf-8")

    source_meta = {
        "doc_slug": slug,
        "rel_path": str(rel_path),
        "format": parser_meta.get("format", ""),
        "parser": parser_meta.get("parser", ""),
        "parser_version": parser_meta.get("parser_version", ""),
        "title": _infer_title(md_text, abs_path),
        "ingested_at": _iso_now(),
    }
    chunks = chunker.chunk_markdown(md_text, source_meta=source_meta)
    chunk_records: list[dict[str, Any]] = []
    for c in chunks:
        chunk_path = chunker.write_chunk(
            chunk_dir=chunk_dir,
            chunk_index=c["chunk_index"],
            text=c["text"],
            source_meta=source_meta,
            section=c["section"],
            total_chunks=c["total_chunks"],
            token_estimate=c["token_estimate"],
            content_hash=c["content_hash"],
            tags=_infer_tags(rel_path, md_text),
        )
        chunk_records.append({
            "chunk_index": c["chunk_index"],
            "total_chunks": c["total_chunks"],
            "chunk_path": str(chunk_path),
            "content_hash": c["content_hash"],
            "token_estimate": c["token_estimate"],
            "section": c["section"],
        })
    meta.upsert_chunks(source_id, chunk_records)

    meta.update_source_status(
        source_id,
        status="parsed",
        parsed_path=parsed_path,
        chunk_dir=chunk_dir,
        chunk_count=len(chunk_records),
    )


def _infer_title(md_text: str, abs_path: Path) -> str:
    """First '#' or '##' heading if present, else filename stem."""
    for line in md_text.splitlines()[:50]:
        if line.startswith("# ") or line.startswith("## "):
            return line.lstrip("#").strip()[:200]
    return abs_path.stem


def _infer_tags(rel_path: Path, md_text: str) -> list[str]:
    """Top-level folder name(s) become tags. Cheap, useful for retrieval."""
    parts = rel_path.parts[:-1]
    return [p.lower().replace(" ", "-") for p in parts if not p.startswith(".")]


def _iso_now() -> str:
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def full_ingest_pass(*, roots: Iterable[Path] | None = None) -> dict[str, Any]:
    """Scan + process all sources. Convenience for one-shot ingestion.

    Returns a summary dict with counts and duration.
    """
    config.init_dirs()
    t0 = time.time()
    scan_and_register(roots=roots)
    counts = process_pending(roots=roots)
    counts["duration_seconds"] = round(time.time() - t0, 2)
    return counts
