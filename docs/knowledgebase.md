# Knowledge Base

> **Status:** Production. Wired into the chat agent (`src/agent_loop.py`) as a
> retrieval-augmented context that grounds every employee question in the
> company's source documents.

The KB ingests files from `~/knowledgebase/` (and any additional source roots
in `data/knowledgebase/config.json`), chunks them into ~512-token sections,
embeds with a strong open model, and serves hybrid retrieval (BM25 + dense
vectors + cross-encoder rerank) so the agent can answer any question with
citations to the exact source.

The agent will say **"I don't have that in my reference material"** rather than
invent an answer when the KB has no confident match.

---

## Why this exists

Previously the agent answered from `AGENTS.md` skills (181 hand-curated
markdown files) — fine for a handful of high-value procedures, but
description-matching does not scale to thousands of pages of source material.
The KB replaces that with proper hybrid retrieval over the actual source
documents, so employees can ask natural-language questions and get a
grounded, cited answer.

## Architecture

```
                  ┌────────────────────────────────────────────┐
                  │  Source of truth (~/knowledgebase/)       │
                  │  PDFs, .md, .txt, .csv (transcripts, etc) │
                  └────────────────────┬───────────────────────┘
                                       │  watcher (FSEvents) / scanner
                                       ▼
                  ┌────────────────────────────────────────────┐
                  │  Parsers (Docling / pypdf / csv / md / txt)│
                  │  -> cleaned Markdown + YAML frontmatter    │
                  └────────────────────┬───────────────────────┘
                                       │  chunker (section-aware, ~512 tok)
                                       ▼
                  ┌────────────────────────────────────────────┐
                  │  data/knowledgebase/                       │
                  │  parsed/   chunks/   inbox/                │
                  │  index/    embeddings/   meta.sqlite       │
                  └────────────────────┬───────────────────────�
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
  ChromaDB collection           bm25s keyword index         .npy embedding cache
  (dense vectors)               (lexical match)            (skip re-embedding)
        └──────────────────────────────┼──────────────────────────────┘
                                       │
                                       ▼
              ┌─────────────────────────────────────────┐
              │  4-stage retrieval                       │
              │  1. dense (ChromaDB cosine)              │
              │  2. BM25 (bm25s, normalized)             │
              │  3. RRF fusion -> top ~30 candidates     │
              │  4. cross-encoder rerank -> top 5        │
              │  5. confidence gate (rerank sigmoid)     │
              └────────────────────┬────────────────────┘
                                   │
                                   ▼
              ┌─────────────────────────────────────────┐
              │  src/agent_loop.py injection              │
              │  <knowledge_base> block w/ [1] [2]...   │
              │  in an untrusted_context_message         │
              │  (user role, metadata.trusted=False)     │
              └─────────────────────────────────────────┘
```

## Models (best quality, fully local)

| Role | Model | Size | Why |
|---|---|---|---|
| Embedding | `nomic-ai/nomic-embed-text-v1.5` | 137M params, 768-dim | MTEB ~62, 8K context, MIT. Best single-vector English embedder we can run without a GPU. |
| Reranker  | `BAAI/bge-reranker-v2-m3` | 568M params | Multilingual cross-encoder, MTEB-R ~58. The single biggest precision win in hybrid RAG. |
| Keyword | `bm25s` (BM25 Okapi) | — | Fastest pure-Python BM25 in 2026. ~10k chunks/sec indexing. |

Both embedding models run via `fastembed`/`transformers` (ONNX backend,
CPU-only, no GPU required). Swap via env vars without code changes:

```bash
export ODYSSEUS_KB_EMBED_MODEL="BAAI/bge-small-en-v1.5"   # ~5x faster, 384-dim, slightly weaker
export ODYSSEUS_KB_RERANK_MODEL="cross-encoder/ms-marco-MiniLM-L-12-v2"  # smaller reranker
python -m scripts.kb.reindex
```

## Storage format (human-readable)

The KB is a directory tree, fully browsable with `ls`/`grep`/your editor:

```
data/knowledgebase/
├── parsed/                              # generated, readable Markdown
│   └── policies--return-polices/
│       └── policies--return-polices.md
├── chunks/                              # generated, chunked + frontmatter
│   └── policies--return-polices/
│       ├── chunk-000-sha256:a8a9a4ff.md
│       ├── chunk-001-sha256:d7717e2c.md
│       └── chunk-002-sha256:46cfdd7d.md
├── inbox/                               # drop-here folder for ad-hoc files
├── index/
│   ├── chroma/<collection-uuid>/        # ChromaDB persistent storage
│   ├── embeddings/s{N}-c{N}.npy         # cached vectors (float32)
│   ├── bm25.pkl                          # keyword index + corpus
│   └── meta.sqlite                        # source + chunk metadata
└── config.json                           # KB settings (auto-created on first run)
```

Each chunk file is a Markdown doc with YAML frontmatter (self-describing
provenance):

```markdown
---
source_doc: policies--return-polices
source_path: policies/return-polices.md
source_type: markdown
title: "return-polices"
section: (untitled)
page:
chunk_index: 0
total_chunks: 3
token_estimate: 391
content_hash: sha256:a8a9a4ff...
ingested_at: 2026-08-04T23:18:09+00:00
parser: pass-through
parser_version:
tags: [policies]
---

# Refund policy
...
```

## How retrieval works — anti-hallucination by construction

The system enforces a **two-mode grounding contract** that depends on
whether the question is about OHS or a general topic:

| Mode | Trigger | Required behavior |
|---|---|---|
| **OHS mode** | KB returns a confident match (>=0.3 rerank score) | Answer ONLY from the KB chunks. Cite every non-trivial claim with `[citation: N]`. |
| **OHS mode (missing data)** | KB returns no confident match AND question is about OHS/products/lab tests/policies | Reply with `I don't have that in my reference material. Would you like me to route this to support?` Do NOT invent company facts. |
| **Web-search mode** | KB returns no confident match AND question is clearly NOT about OHS (weather, news, science, current events, geography, sports, etc.) | Call `web_search` or `web_fetch` to find a validated answer. Cite the source URL(s) in the reply. Do NOT answer from training data. |

Every chat turn goes through these defenses, in order:

1. **Mandatory retrieval.** When the chat is in KB mode (default ON for
   the OHS deployment), the system prompt begins with a `<knowledge_base>`
   block of retrieved chunks. The model literally cannot respond without
   seeing them first. The block carries MANDATORY rules describing whether
   to answer from KB, refuse with the canonical phrase, or web-search.

2. **Confidence gate.** If no chunk reranks above the threshold (default
   `0.3`), the system prompt contains an explicit "no confident results"
   instruction. The model then decides per the table above: refuse (OHS)
   or web-search (non-OHS).

3. **Mandatory citations.** The system prompt requires `[citation: N]`
   after every non-trivial claim when the KB is in use. Citations resolve
   to real chunk IDs, which resolve to real source documents.
   For web-search answers, the model must cite the source URL(s).

4. **Audit log.** Every retrieval is recorded in
   `data/knowledgebase/index/meta.sqlite` (table `retrieval_log`) so any
   past answer can be traced back to what the model was shown.

The system prompt rule that enforces this lives in both `_AGENT_RULES`
and `_API_AGENT_RULES` in `src/agent_loop.py`. It says, in summary:

> When the conversation contains a `<knowledge_base>` block of retrieved
> reference material, answer using ONLY that material, cite each
> non-trivial claim with `[citation: N]`, and say exactly "I don't have
> that in my reference material" when the block doesn't answer the
> question. Do not invent company facts, product details, lab
> interpretations, policies, or pricing.

## Daily use

### Initial ingest (one time)

```bash
# Parse + chunk all configured sources
python -m scripts.kb.ingest

# Embed (parallel) + build ChromaDB + BM25
python -m scripts.kb.index
```

For ~3000 chunks on a Mac mini, the embed step takes ~5 min with 6 workers.

### Continuous ingestion (drop files in, done)

```bash
# Foreground watcher (Ctrl-C to stop)
python -m scripts.kb.watch

# Or run as a one-shot scan + index (use from cron / launchd)
python -m scripts.kb.watch --once

# Or via HTTP from the admin UI:
curl -X POST http://localhost:7860/api/kb/reindex
```

The watcher uses FSEvents on macOS (instant) and watchdog on Linux.
Adding a file to `~/knowledgebase/` causes it to appear in the KB within
~1 second when the watcher is running.

### Test a query from the CLI

```bash
python -m scripts.kb.query "What's the return policy for opened products?"
python -m scripts.kb.query "What's the return policy for opened products?" --show-block
```

The `--show-block` flag prints the exact prompt block the LLM would see.

### Health check

```bash
python -m scripts.kb.stats
```

Returns source counts, chunk counts, index sizes, model names, current
threshold, and retrieval history.

## HTTP API

All routes are auth-protected (same as the rest of Odysseus).

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/kb/query` | POST | Run retrieval. Body: `{query, top_k?}`. Returns ranked chunks + citations + ready-to-inject `prompt_block`. |
| `/api/kb/stats` | GET | Health summary. |
| `/api/kb/reindex` | POST | Re-scan + re-index. Idempotent. |

## Configuration

Edit `data/knowledgebase/config.json` (auto-created on first run with
defaults). All keys are optional; missing keys fall back to defaults in
`src/knowledgebase/config.py`.

```json
{
  "source_roots": ["~/knowledgebase", "~/Documents/ohs"],
  "embed_model": "nomic-ai/nomic-embed-text-v1.5",
  "rerank_model": "BAAI/bge-reranker-v2-m3",
  "embed_batch_size": 64,
  "embed_parallel_workers": 0,
  "rerank_batch_size": 32,
  "chunk_target_tokens": 512,
  "chunk_overlap_tokens": 80,
  "default_top_k": 20,
  "rerank_top_k": 5,
  "confidence_threshold": 0.3,
  "chroma_collection": "kb_chunks_v1"
}
```

| Setting | Default | Notes |
|---|---|---|
| `source_roots` | `["~/knowledgebase"]` | Watched directories. `~/knowledgebase` and `data/knowledgebase/inbox` are always added implicitly. |
| `confidence_threshold` | `0.3` | Below this, the system answers "I don't have that". Raise to be stricter, lower to be more permissive. |
| `embed_parallel_workers` | `0` (=auto) | Set to `1` to force serial embedding. Set to `0` to auto-pick `min(cpu_count//2, 6)`. |

## How the post-processor enforces grounding

Models don't always follow the rule even when KB content is in the prompt.
The post-processor in `src/knowledgebase/grounding.py` is a
belt-and-suspenders check that runs after the model streams its response.

Every chat turn is one of several outcomes the post-processor checks,
matched against the two-mode grounding contract:

| KB retrieval | Model behavior | Post-processor action |
|---|---|---|
| Has confident answer | Cites with `[citation: N]` | Compliant. No action. |
| Has confident answer | Doesn't cite | **Rewrite** with citation-grounded excerpt from retrieved chunks. Log WARNING audit. |
| No confident answer | Says refusal phrase (OHS topic) | Compliant. No action. |
| No confident answer | Cites a web source (non-OHS topic) | Compliant. No action. |
| No confident answer | Hallucinates | **Force** canonical refusal. Log WARNING audit. |
| Errored (SQLite / Chroma / etc.) | Says refusal phrase OR cites web source | Compliant. No action. |
| Errored | Hallucinates | **Force** refusal with "KB unavailable" note. |
| Skipped (guide_only mode) | Anything | Compliant (no KB context to enforce). |

The post-processor's rewrite is streamed to the user as additional deltas
before `[DONE]`, so the user sees both the model's response and the
grounded correction when applicable. The corrected text is also what gets
persisted as the assistant message and shown in chat history.

Audit log: every non-compliant outcome emits a WARNING-level log line
that includes the query, confidence, issue type, and response length.
Search `data/logs/` for `kb-grounding` to find historical corrections.

Health check: `grounding.check_kb_health()` returns a `HealthStatus` with
sources_indexed, chroma_items, bm25_exists, and any issues. Call it
periodically (or from a startup hook) to fail fast on broken indexes.

End-to-end test: `venv/bin/python tests/test_kb_grounding.py` runs all
7 unit scenarios + a live chat test against the running Odysseus
service. Exits non-zero if any scenario regresses.

## Operational notes

### Idempotency

Every source has a content hash (SHA-256 of file contents). Re-running
ingest on an unchanged file is a no-op. Editing a file flips its status
back to `pending` and triggers re-chunk + re-embed on the next pass.

### Chunk size & large tables

CSVs with very wide columns (>25) are auto-pruned to keep only columns
whose header suggests informative content (Title, Body, Description,
etc.). For tables with >25 columns, chunks cap at 4 rows. For tables
with ≤6 columns, up to 25 rows. Per-chunk token target is 512 with 15%
overlap, max 4096 tokens.

### PDFs

`Docling` (IBM) is the primary PDF parser — best-in-class for tables,
layouts, multi-column layouts, and headers/footers. Falls back to
`pypdf` if Docling isn't installed.

### Memory

- nomic-embed-v1.5: ~250 MB per worker process. With `embed_parallel_workers=6`
  expect ~1.5 GB peak during indexing.
- ChromaDB: ~1.5 GB on disk for 100k chunks.
- BM25 pickle: ~200–400 MB in RAM at query time.

### Performance

On a Mac mini M-series (4–8 cores):

| Stage | Time for 3000 chunks |
|---|---|
| Parse (PDF/MD/CSV) | ~5 sec |
| Chunk | ~3 sec |
| Embed (6 workers, nomic-embed-v1.5) | ~5 min |
| Build ChromaDB + BM25 | ~10 sec |
| Query (warm) | ~0.5 sec |

## Troubleshooting

### "No confident results" for things that should match

```bash
# See what chunks are being retrieved and at what confidence:
python -m scripts.kb.query "the question you're asking"

# If top chunks are unrelated, the KB may need more content. Add source
# files to ~/knowledgebase/ and let the watcher pick them up.

# If top chunks look right but confidence is below 0.3, lower the threshold
# in data/knowledgebase/config.json: "confidence_threshold": 0.2

# If retrieval quality is generally poor, swap to a stronger embedding model:
export ODYSSEUS_KB_EMBED_MODEL="nomic-ai/nomic-embed-text-v1.5"
python -m scripts.kb.reindex
```

### Index is stale

```bash
# Force a full rescan + reindex
rm -rf data/knowledgebase/index/embeddings
python -m scripts.kb.reindex

# Or via HTTP
curl -X POST http://localhost:7860/api/kb/reindex
```

### The agent invents facts anyway

The grounding rule in `src/agent_loop.py` says the model must answer only
from `<knowledge_base>`. If the model still invents, three likely causes:

1. **`<knowledge_base>` is empty** (no chunks above threshold) but the
   model didn't trigger the "no confident results" fallback. Check
   `python -m scripts.kb.query "the question"` — if it returns no
   chunks, the agent should fall back. If `has_answer: True` but chunks
   look unrelated, lower `confidence_threshold` and re-index.

2. **System prompt cache is stale.** Clear by restarting the Odysseus
   service. The cache lives in `_cached_base_prompt` in `agent_loop.py`.

3. **The model itself doesn't follow the rule reliably.** If using a
   smaller local model, switch to a larger one. The default
   `MiniMax-M3` in settings.json is fine; small models (4B and below)
   sometimes ignore grounding rules.

## Code map

```
src/knowledgebase/
├── __init__.py
├── config.py            # paths, models, thresholds (defaults + config.json merge)
├── hash.py              # SHA-256 helpers (used for idempotency)
├── meta.py              # SQLite index: sources, chunks, retrieval_log
├── parsers.py           # file → Markdown (Docling, pypdf, csv, md, txt, html)
├── chunker.py           # Markdown → chunks with YAML frontmatter
├── scanner.py           # find new/changed files + run them through ingest
├── embed_parallel.py    # multiprocessing worker for fastembed
├── indexer.py           # embed + ChromaDB + bm25s
├── retriever.py         # hybrid (BM25+dense) → RRF → rerank → confidence
└── watcher.py           # watchdog/FSEvents-based continuous ingestion

scripts/kb/
├── ingest.py            # CLI: parse + chunk
├── index.py             # CLI: embed + index
├── watch.py             # CLI: long-running watcher
├── query.py             # CLI: smoke-test retrieval
└── stats.py             # CLI: health check

routes/knowledgebase_routes.py   # /api/kb/query, /api/kb/stats, /api/kb/reindex
```

## Migration from skill-based knowledge

The 181 `SKILL.md` files that previously served as the knowledge source
have been moved to `data/skills/.archived-20260804/`. The new KB replaces
them with proper retrieval. To restore any archived skill as a hard
override (useful for things like the no-fabrication rule that must always
fire), copy it back into `data/skills/<category>/<name>/SKILL.md`. Skills
load on demand via the existing skills mechanism; the KB covers
everything else.
