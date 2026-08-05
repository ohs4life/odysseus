"""Parallel embedding via multiprocessing.

The onnx embedding models (nomic-embed-v1.5 etc.) are CPU-bound but each
TextEmbedding instance uses all available cores via its internal ONNX session.
A single model can saturate ~2-3 cores; spawning extra workers can use the
remaining cores to roughly double throughput on a 4-core machine.

For nomic-embed-v1.5 on a Mac mini this brings 3142 chunks down from ~16
minutes (serial) to ~4-6 minutes (4 workers), at the cost of ~4x peak RAM.

Embeddings are written to .npy files in data/knowledgebase/index/embeddings/
so they can be re-loaded into ChromaDB without re-running the model.
"""

from __future__ import annotations

import logging
import multiprocessing as mp
import os
import time
from pathlib import Path
from typing import Iterable

log = logging.getLogger("odysseus.kb.embed_parallel")


def _worker_main(work: list[tuple[str, list[str]]]) -> list[tuple[str, int]]:
    """Worker: embed a batch of (npy_path, text) pairs.

    Returns [(path, dim), ...] on success. Loads the model fresh per worker
    (fastembed instances are not fork-safe).
    """
    import numpy as np
    from fastembed import TextEmbedding

    model_name = os.environ.get("ODYSSEUS_KB_EMBED_MODEL") or (
        "nomic-ai/nomic-embed-text-v1.5"
    )
    model = TextEmbedding(model_name=model_name)
    out: list[tuple[str, int]] = []
    for path, text in work:
        vecs = list(model.embed([text]))
        if not vecs:
            continue
        np.save(path, np.array(vecs[0], dtype=np.float32))
        out.append((path, len(vecs[0])))
    return out


def _auto_workers() -> int:
    """Pick a worker count that balances CPU usage vs RAM.

    Returns min(cpu_count, max(1, cpu_count // 2)). Cap at 6 because each
    worker loads the model (~250MB for nomic-embed-v1.5) and we don't want
    to exhaust RAM on small machines.
    """
    cpu = os.cpu_count() or 4
    return max(1, min(6, cpu // 2))


def embed_parallel(
    items: list[tuple[str, str]],
    *,
    workers: int = 0,
    batch_size: int = 64,
) -> dict[str, int]:
    """Embed (npy_path, text) pairs across multiple processes.

    `items` is the full list. We split it into `workers` chunks. Each worker
    embeds its chunk in-process. Workers are spawned (not forked) so the
    onnx session is clean per process.

    Returns a {npy_path: dim} dict for everything that was successfully
    embedded (already-existing files are skipped before workers run).
    """
    if workers <= 0:
        workers = _auto_workers()
    if workers == 1 or len(items) <= batch_size:
        return dict(_worker_main(items))

    log.info("embed_parallel: %d items across %d workers", len(items), workers)
    t0 = time.time()
    # Split into N roughly-equal chunks.
    chunks: list[list[tuple[str, str]]] = [[] for _ in range(workers)]
    for i, item in enumerate(items):
        chunks[i % workers].append(item)

    # Use spawn to avoid inheriting parent's onnx / chromadb state.
    ctx = mp.get_context("spawn")
    with ctx.Pool(processes=workers) as pool:
        results = pool.map(_worker_main, chunks)

    flat: dict[str, int] = {}
    for r in results:
        for path, dim in r:
            flat[path] = dim
    log.info("embed_parallel: %d items in %.1fs", len(flat), time.time() - t0)
    return flat
