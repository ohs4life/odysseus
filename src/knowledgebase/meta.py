"""SQLite metadata database — the canonical index of what's been ingested.

Tracks every source file: its content hash, what parser ran, where the parsed
Markdown and chunks live, embedding status. The indexer reads this to know
what's new vs. already embedded; the retriever reads this to resolve
chunk_id -> source_path for citations.
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any

from . import config

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_root     TEXT    NOT NULL,
    rel_path        TEXT    NOT NULL,
    absolute_path   TEXT    NOT NULL,
    content_hash    TEXT    NOT NULL,
    size_bytes      INTEGER NOT NULL,
    mtime           REAL    NOT NULL,
    parser          TEXT,
    parsed_path     TEXT,
    chunk_dir       TEXT,
    chunk_count     INTEGER DEFAULT 0,
    embedded_count  INTEGER DEFAULT 0,
    embedded_at     REAL,
    status          TEXT    NOT NULL DEFAULT 'pending',
    error           TEXT,
    discovered_at   REAL    NOT NULL,
    updated_at      REAL    NOT NULL,
    UNIQUE(source_root, rel_path)
);
CREATE INDEX IF NOT EXISTS idx_sources_status ON sources(status);
CREATE INDEX IF NOT EXISTS idx_sources_hash   ON sources(content_hash);

CREATE TABLE IF NOT EXISTS chunks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id       INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    total_chunks    INTEGER NOT NULL,
    chunk_path      TEXT    NOT NULL,
    content_hash    TEXT    NOT NULL,
    token_estimate  INTEGER NOT NULL,
    section         TEXT,
    UNIQUE(source_id, chunk_index)
);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id);

CREATE TABLE IF NOT EXISTS retrieval_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              REAL    NOT NULL,
    query           TEXT    NOT NULL,
    top_chunks      TEXT    NOT NULL,    -- JSON list of {chunk_id, score}
    confidence      REAL,
    answer_provided INTEGER NOT NULL     -- 1 = answer, 0 = "I don't know"
);
CREATE INDEX IF NOT EXISTS idx_retrieval_ts ON retrieval_log(ts);
"""


def _connect() -> sqlite3.Connection:
    """Open a connection with row factory + foreign keys.

    check_same_thread=False because FastAPI runs request handlers in a
    threadpool — the same module-level connection gets reused across threads.
    SQLite is process-safe enough for our read-mostly workload; WAL mode
    handles concurrent writes cleanly.
    """
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.META_DB, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    """Lazy-init the singleton connection. Safe to call repeatedly."""
    global _conn
    if _conn is None:
        _conn = _connect()
        _conn.executescript(_SCHEMA)
    return _conn


def reset_conn_for_tests() -> None:
    """Close the singleton (used by tests that swap META_DB path)."""
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


# ----- Sources -----

def upsert_source(
    *,
    source_root: Path,
    rel_path: Path,
    absolute_path: Path,
    content_hash: str,
    size_bytes: int,
    mtime: float,
    parser: str | None = None,
    parsed_path: Path | None = None,
    chunk_dir: Path | None = None,
) -> int:
    """Insert or update a source row. Returns the source id.

    Preserves parser/parsed_path/chunk_dir/embedding state when the content
    hash matches (re-ingest of identical content is a no-op). When the hash
    changes (file edited), resets status to 'pending' so it gets re-processed.
    """
    conn = get_conn()
    now = time.time()
    cur = conn.execute(
        "SELECT id, content_hash FROM sources WHERE source_root=? AND rel_path=?",
        (str(source_root), str(rel_path)),
    )
    row = cur.fetchone()
    if row is None:
        cur = conn.execute(
            """INSERT INTO sources
               (source_root, rel_path, absolute_path, content_hash, size_bytes, mtime,
                parser, parsed_path, chunk_dir, status, discovered_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
            (
                str(source_root), str(rel_path), str(absolute_path), content_hash,
                size_bytes, mtime, parser,
                str(parsed_path) if parsed_path else None,
                str(chunk_dir) if chunk_dir else None,
                now, now,
            ),
        )
        return int(cur.lastrowid)
    existing_id, existing_hash = row["id"], row["content_hash"]
    if existing_hash == content_hash:
        # Same content — update mtime/size/path in case the file moved, keep state.
        conn.execute(
            """UPDATE sources SET absolute_path=?, size_bytes=?, mtime=?, updated_at=?
               WHERE id=?""",
            (str(absolute_path), size_bytes, mtime, now, existing_id),
        )
    else:
        # Content changed — reset for re-processing.
        conn.execute(
            """UPDATE sources SET content_hash=?, size_bytes=?, mtime=?,
                                  parser=?, parsed_path=?, chunk_dir=?,
                                  chunk_count=0, embedded_count=0, embedded_at=NULL,
                                  status='pending', error=NULL, updated_at=?
               WHERE id=?""",
            (
                content_hash, size_bytes, mtime, parser,
                str(parsed_path) if parsed_path else None,
                str(chunk_dir) if chunk_dir else None,
                now, existing_id,
            ),
        )
    return existing_id


def update_source_status(
    source_id: int,
    *,
    status: str,
    error: str | None = None,
    parsed_path: Path | None = None,
    chunk_dir: Path | None = None,
    chunk_count: int | None = None,
) -> None:
    """Update processing status for a source."""
    conn = get_conn()
    sets = ["status=?", "updated_at=?", "error=?"]
    vals: list[Any] = [status, time.time(), error]
    if parsed_path is not None:
        sets.append("parsed_path=?")
        vals.append(str(parsed_path))
    if chunk_dir is not None:
        sets.append("chunk_dir=?")
        vals.append(str(chunk_dir))
    if chunk_count is not None:
        sets.append("chunk_count=?")
        vals.append(chunk_count)
    vals.append(source_id)
    conn.execute(f"UPDATE sources SET {', '.join(sets)} WHERE id=?", vals)


def mark_embedded(source_id: int, count: int) -> None:
    """Mark a source as embedded with N chunks in the vector index."""
    conn = get_conn()
    conn.execute(
        """UPDATE sources SET embedded_count=?, embedded_at=?, status='indexed',
                              updated_at=?, error=NULL
           WHERE id=?""",
        (count, time.time(), time.time(), source_id),
    )


def get_source(source_id: int) -> dict[str, Any] | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM sources WHERE id=?", (source_id,)).fetchone()
    return dict(row) if row else None


def find_source_by_hash(content_hash: str) -> dict[str, Any] | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM sources WHERE content_hash=? ORDER BY id DESC LIMIT 1",
        (content_hash,),
    ).fetchone()
    return dict(row) if row else None


def list_pending_sources(*, limit: int = 1000) -> list[dict[str, Any]]:
    """Sources that need (re-)processing: status='pending' or 'error'."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT * FROM sources
           WHERE status IN ('pending', 'error')
           ORDER BY id ASC LIMIT ?""",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def list_indexed_sources() -> list[dict[str, Any]]:
    """All sources that have been fully ingested AND indexed."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM sources WHERE status='indexed' ORDER BY id ASC"
    ).fetchall()
    return [dict(r) for r in rows]


def list_all_sources() -> list[dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM sources ORDER BY id ASC").fetchall()
    return [dict(r) for r in rows]


# ----- Chunks -----

def upsert_chunks(source_id: int, chunks: list[dict[str, Any]]) -> None:
    """Replace all chunks for a source with the given list.

    Each chunk dict has: chunk_index, total_chunks, chunk_path, content_hash,
    token_estimate, section.
    """
    conn = get_conn()
    # Wipe and re-insert — chunks are derived state, always replaced together.
    conn.execute("DELETE FROM chunks WHERE source_id=?", (source_id,))
    conn.executemany(
        """INSERT INTO chunks
           (source_id, chunk_index, total_chunks, chunk_path, content_hash,
            token_estimate, section)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                source_id,
                c["chunk_index"],
                c["total_chunks"],
                c["chunk_path"],
                c["content_hash"],
                c["token_estimate"],
                c.get("section"),
            )
            for c in chunks
        ],
    )


def list_all_chunks() -> list[dict[str, Any]]:
    """Every chunk in the KB, joined with its source. Used by the indexer."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT chunks.*, sources.rel_path AS source_rel_path,
                  sources.absolute_path AS source_abs_path,
                  sources.source_root AS source_root
           FROM chunks JOIN sources ON chunks.source_id = sources.id
           WHERE sources.status = 'indexed'
           ORDER BY chunks.id ASC"""
    ).fetchall()
    return [dict(r) for r in rows]


def list_chunks_for_source(source_id: int) -> list[dict[str, Any]]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM chunks WHERE source_id=? ORDER BY chunk_index ASC",
        (source_id,),
    ).fetchall()
    return [dict(r) for r in rows]


# ----- Retrieval log -----

def log_retrieval(
    *, query: str, top_chunks: list[dict[str, Any]],
    confidence: float | None, answer_provided: bool,
) -> None:
    """Record a retrieval event for audit/observability."""
    import json
    conn = get_conn()
    conn.execute(
        """INSERT INTO retrieval_log
           (ts, query, top_chunks, confidence, answer_provided)
           VALUES (?, ?, ?, ?, ?)""",
        (
            time.time(), query[:2000], json.dumps(top_chunks),
            confidence, 1 if answer_provided else 0,
        ),
    )


def retrieval_stats(*, since_ts: float | None = None) -> dict[str, Any]:
    conn = get_conn()
    where = "WHERE ts >= ?" if since_ts else ""
    params: tuple[Any, ...] = (since_ts,) if since_ts else ()
    row = conn.execute(
        f"""SELECT COUNT(*) AS total,
                   SUM(answer_provided) AS answered,
                   AVG(confidence) AS avg_confidence
            FROM retrieval_log {where}""",
        params,
    ).fetchone()
    return {
        "total": row["total"] or 0,
        "answered": row["answered"] or 0,
        "no_answer": (row["total"] or 0) - (row["answered"] or 0),
        "avg_confidence": row["avg_confidence"],
    }
