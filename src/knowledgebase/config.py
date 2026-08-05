"""Knowledge base configuration: paths, models, thresholds.

Settings can be overridden via data/knowledgebase/config.json (auto-created
on first run with defaults). Read once at import time, cached.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# ----- Root paths -----

ODYSSEUS_ROOT = Path(os.environ.get("ODYSSEUS_ROOT", "/Users/ai/odysseus")).resolve()
DATA_DIR = ODYSSEUS_ROOT / "data"
KB_ROOT = DATA_DIR / "knowledgebase"

# Source roots: paths the scanner/watcher monitor for new content.
# The primary is the user's ~/knowledgebase/. Inbox is a drop-here folder
# inside the odysseus data dir for files that need to bypass the user's folder.
DEFAULT_SOURCE_ROOTS: list[Path] = [
    Path.home() / "knowledgebase",
    KB_ROOT / "inbox",
]

# Generated artifact directories (relative to KB_ROOT)
PARSED_DIR = KB_ROOT / "parsed"
CHUNKS_DIR = KB_ROOT / "chunks"
INDEX_DIR = KB_ROOT / "index"
META_DB = INDEX_DIR / "meta.sqlite"
BM25_PATH = INDEX_DIR / "bm25.pkl"
CONFIG_PATH = KB_ROOT / "config.json"

# ChromaDB server uses existing persistent client. New collection for the KB
# so we don't collide with existing personal_docs / memories / tool_index collections.
CHROMA_PATH = DATA_DIR / "chroma"
CHROMA_COLLECTION = "kb_chunks_v1"

# ----- Models (verified best-of-class for local Mac mini, all via fastembed) -----

# Best-quality open models (verified Jan 2026):
# - nomic-embed-text-v1.5: 137M params, 768-dim, MTEB ~62, 8K context.
#   MIT licensed. The best single-vector English embedding model we can run
#   locally without a GPU. ~2.5x slower than BGE-small on CPU but materially
#   better retrieval quality.
# - bge-reranker-v2-m3: multilingual cross-encoder reranker, MTEB-R ~58.
#   The strongest open reranker. Compensates for any weakness in the
#   embedding stage and is the single biggest precision win in hybrid RAG.
EMBED_MODEL = "nomic-ai/nomic-embed-text-v1.5"
RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
# Fallback if docling isn't available:
PRIMARY_PDF_PARSER = "docling"
FALLBACK_PDF_PARSER = "pypdf"

# ----- Chunking -----

CHUNK_TARGET_TOKENS = 512
CHUNK_OVERLAP_TOKENS = 80            # ~15% overlap
CHUNK_MIN_TOKENS = 64                # drop tiny trailing chunks
CHARS_PER_TOKEN = 4                  # rough approximation for English text

# ----- Retrieval -----

DEFAULT_TOP_K = 20                    # candidates after hybrid + rerank
RERANK_TOP_K = 5                      # final chunks returned
CONFIDENCE_THRESHOLD = 0.3            # below this, say "I don't have that"
RRF_K = 60                            # standard RRF constant

# ----- Embedding performance -----
EMBED_BATCH_SIZE = 64                 # batch size inside each worker
EMBED_PARALLEL_WORKERS = 0            # 0 = auto-detect from CPU count
RERANK_BATCH_SIZE = 32

# ----- File handling -----

SKIP_FILENAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
SKIP_PREFIXES = (".", "~$")            # hidden + Office lock files
SUPPORTED_EXTS = {".md", ".markdown", ".txt", ".csv", ".pdf", ".html", ".htm"}

# ----- Defaults merged with config.json -----

_DEFAULTS: dict[str, Any] = {
    "source_roots": [str(p) for p in DEFAULT_SOURCE_ROOTS],
    "embed_model": EMBED_MODEL,
    "rerank_model": RERANK_MODEL,
    "embed_batch_size": EMBED_BATCH_SIZE,
    "embed_parallel_workers": EMBED_PARALLEL_WORKERS,
    "rerank_batch_size": RERANK_BATCH_SIZE,
    "chunk_target_tokens": CHUNK_TARGET_TOKENS,
    "chunk_overlap_tokens": CHUNK_OVERLAP_TOKENS,
    "default_top_k": DEFAULT_TOP_K,
    "rerank_top_k": RERANK_TOP_K,
    "confidence_threshold": CONFIDENCE_THRESHOLD,
    "chroma_collection": CHROMA_COLLECTION,
}


def _load_user_config() -> dict[str, Any]:
    """Merge defaults with user config.json (deep-merge at top level)."""
    if CONFIG_PATH.exists():
        try:
            user = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            user = {}
    else:
        user = {}
    merged = dict(_DEFAULTS)
    merged.update({k: v for k, v in user.items() if k in _DEFAULTS})
    # Always normalize source_roots to Path objects (no-op if already Paths).
    merged["source_roots"] = [Path(p).expanduser() for p in merged["source_roots"]]
    return merged


_SETTINGS: dict[str, Any] = _load_user_config()


def get(key: str) -> Any:
    """Get a config value (read-only access)."""
    return _SETTINGS[key]


def all() -> dict[str, Any]:
    """Snapshot of all settings (for /api/kb/stats)."""
    out = dict(_SETTINGS)
    out["source_roots"] = [str(p) for p in out["source_roots"]]
    return out


def init_dirs() -> None:
    """Ensure all KB directories exist. Idempotent."""
    KB_ROOT.mkdir(parents=True, exist_ok=True)
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    (KB_ROOT / "inbox").mkdir(parents=True, exist_ok=True)


def reset_for_tests() -> None:
    """Reset the cached settings (used by tests after editing config.json)."""
    global _SETTINGS
    _SETTINGS = _load_user_config()
