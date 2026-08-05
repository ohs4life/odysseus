"""Content hashing for idempotent ingestion."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path, *, chunk_bytes: int = 1 << 20) -> str:
    """SHA-256 of file contents, hex digest with `sha256:` prefix.

    Reads in 1MB chunks so it works on huge files without loading them in RAM.
    Returns the canonical content hash used everywhere (DB rows, chunk filenames,
    parsed-file sidecars) so the same file always produces the same identifier.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_bytes)
            if not chunk:
                break
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def sha256_text(text: str) -> str:
    """SHA-256 of a text string (for chunk content hashes)."""
    h = hashlib.sha256()
    h.update(text.encode("utf-8"))
    return f"sha256:{h.hexdigest()}"


def short_hash(full_hash: str, *, length: int = 12) -> str:
    """Truncated hash for human-readable filenames.

    >>> short_hash('sha256:abcdef1234567890...')
    'sha256:abcdef123456'
    """
    return full_hash[: length + len("sha256:")]
