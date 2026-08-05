"""KB grounding enforcement.

Two layers of defense against hallucination:

1. **Pre-flight (in _build_system_prompt):** Inject a KB context message into
   every chat turn. The message either (a) contains retrieved chunks the
   model must use, (b) tells the model to refuse because the KB had no
   confident answer, or (c) tells the model to refuse because KB retrieval
   errored. The model cannot respond without seeing one of these.

2. **Post-processor (this module):** Verify the model's response against
   the actual retrieval outcome and rewrite if it didn't follow the rule.

The pre-flight alone is not enough. Models (especially smaller ones like
MiniMax-M3) sometimes ignore the system prompt rule and answer from
general knowledge anyway. The post-processor is the belt-and-suspenders:
it inspects the final response and either (a) appends a correction delta,
(b) replaces the response, or (c) logs an audit warning.

Public API:
    enforce_grounding(response_text, retrieval_result, query) -> GroundingCheck
        Inspects the response and returns a verdict + optional corrected text.

    check_kb_health() -> HealthStatus
        Lightweight check that the KB index is reachable. Called before
        chat starts so a broken index fails fast instead of silently
        falling through to "no KB".
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from . import config, meta

log = logging.getLogger("odysseus.kb.grounding")


# Canonical refusal phrase the model is told to use. We also accept variants
# so we don't over-trigger on minor wording differences.
CANONICAL_REFUSAL = (
    "I don't have that in my reference material. "
    "Would you like me to web-search for current info, or route this to support?"
)

# Acceptable variants the post-processor treats as compliant.
# These cover: the canonical refusal, partial refusals ("I can't find X"),
# honest admissions of missing capability ("I don't have access to a web
# fetch tool"), and explicit inability statements.
_REFUSAL_PATTERNS = [
    re.compile(r"i don'?t have that in my reference material", re.IGNORECASE),
    re.compile(r"i don'?t have (?:that|specific|that specific) information", re.IGNORECASE),
    re.compile(r"i don'?t have (?:access|ability|capability|tool)", re.IGNORECASE),
    re.compile(r"i don'?t have (?:live|real[- ]time|current) (?:weather|data|info)", re.IGNORECASE),
    re.compile(r"not (?:in my|in the) reference material", re.IGNORECASE),
    re.compile(r"i (?:can'?t|cannot) find (?:that|this) (?:in|within) (?:my|the) (?:reference|kdb|knowledge)", re.IGNORECASE),
    re.compile(r"i (?:can'?t|cannot) (?:actually |currently )?(?:fetch|retrieve|access|get|check|hit)", re.IGNORECASE),
    re.compile(r"my available tools don'?t include", re.IGNORECASE),
]

# Citation marker: [citation: N] or [citation: N, M, ...]
_CITATION_RE = re.compile(r"\[citation:\s*\d+(?:\s*,\s*\d+)*\s*\]", re.IGNORECASE)


@dataclass
class GroundingCheck:
    """Result of checking one model response against the KB retrieval."""

    compliant: bool                     # True if the response follows the rule
    issue: Optional[str] = None          # Why it's non-compliant (for logging)
    corrected: Optional[str] = None       # Replacement text if not compliant
    confidence: float = 0.0              # Retrieval confidence that drove the check
    retrieval_status: str = "unknown"    # "ok_has_answer", "ok_no_answer", "error", "skipped"


def has_citation(text: str) -> bool:
    """Return True if the response contains at least one citation marker."""
    return bool(_CITATION_RE.search(text or ""))


def has_refusal(text: str) -> bool:
    """Return True if the response contains a compliant refusal phrase."""
    if not text:
        return False
    return any(p.search(text) for p in _REFUSAL_PATTERNS)


# Web source markers the model emits when it cites a web result. We accept
# these as compliant when the KB had no answer (i.e. the model did the right
# thing: web-searched and cited the source).
_WEB_SOURCE_PATTERNS = [
    re.compile(r"https?://[\w\-\.]+\.[a-z]{2,}(/\S*)?", re.IGNORECASE),
    re.compile(r"\bsource:\s*\S+", re.IGNORECASE),
    re.compile(r"\baccording to\b[^.]*?\b(?:\w+\.){1,}", re.IGNORECASE),
    re.compile(r"\[web[\s_-]?source\s*[:\]]", re.IGNORECASE),
]


def has_web_source(text: str) -> bool:
    """Return True if the response cites a web source (URL, 'source: ...', etc.)."""
    if not text:
        return False
    return any(p.search(text) for p in _WEB_SOURCE_PATTERNS)


def enforce_grounding(
    response_text: str,
    retrieval_result,  # RetrievalResult from retriever, or None
    *,
    retrieval_status: str = "unknown",
    web_search_used: bool = False,
) -> GroundingCheck:
    """Verify a model response against KB grounding rules.

    - retrieval_result.has_answer=True and response lacks citation:
      non-compliant. Append the actual retrieved answer so the user sees
      the grounded information, plus the "I should have cited this"
      correction.

    - retrieval_result.has_answer=False and response lacks refusal:
      non-compliant. Replace with the canonical refusal.

    - retrieval_status="error": assume non-compliant (model was told
      to refuse but might have hallucinated). If it didn't refuse, force
      the refusal.

    - web_search_used=True: the model actually called web_search or
      web_fetch during this turn. Accept ANY substantive response as
      compliant — the user explicitly asked for web research and the
      model did it. Don't force the "I don't have that" refusal on top
      of a successful web-searched answer.

    Returns a GroundingCheck with `compliant`, `corrected`, etc.
    """
    text = (response_text or "").strip()
    confidence = getattr(retrieval_result, "confidence", 0.0) if retrieval_result else 0.0

    # Order matters: check "error" and "skipped" status BEFORE checking
    # retrieval_result is None, since an error can coexist with None.
    if retrieval_status == "error":
        # KB retrieval failed. Acceptable behaviors: refuse (OHS), or
        # web-search and cite source (non-OHS). Anything else is non-compliant.
        # ALSO: web_search_used means the model already handled it.
        if web_search_used:
            return GroundingCheck(
                compliant=True,
                confidence=0.0,
                retrieval_status="error",
            )
        if has_refusal(text):
            return GroundingCheck(
                compliant=True,
                confidence=0.0,
                retrieval_status="error",
            )
        if has_web_source(text):
            return GroundingCheck(
                compliant=True,
                confidence=0.0,
                retrieval_status="error",
            )
        log.warning(
            "GROUNDING FAILURE: KB retrieval errored but model did not refuse "
            "OR cite a web source. Forcing canonical refusal. response_len=%d",
            len(text),
        )
        return GroundingCheck(
            compliant=False,
            issue="kb_errored_but_no_refusal_or_web_source",
            corrected=CANONICAL_REFUSAL + " (The knowledge base is temporarily unavailable.)",
            confidence=0.0,
            retrieval_status="error",
        )

    if retrieval_status == "skipped" or (retrieval_result is None and retrieval_status != "error"):
        # KB mode not active for this turn (e.g., guide_only). Nothing to enforce.
        return GroundingCheck(
            compliant=True,
            confidence=0.0,
            retrieval_status="skipped",
        )

    # Retrieval succeeded.
    if getattr(retrieval_result, "has_answer", False):
        if has_citation(text):
            return GroundingCheck(
                compliant=True,
                confidence=confidence,
                retrieval_status="ok_has_answer",
            )
        # Non-compliant: KB had a confident answer but the model didn't cite.
        # Build a correction that quotes the retrieved content with citations.
        log.warning(
            "GROUNDING FAILURE: KB had confident answer (conf=%.3f) but model "
            "response had no [citation: N] marker. response_len=%d",
            confidence, len(text),
        )
        # Append the actual KB content as the citation-grounded answer.
        corrected = _build_cited_answer(text, retrieval_result)
        return GroundingCheck(
            compliant=False,
            issue="kb_had_answer_but_no_citation",
            corrected=corrected,
            confidence=confidence,
            retrieval_status="ok_has_answer",
        )

    # KB had no confident answer. Three acceptable model behaviors:
    #   1. Refuse with the canonical phrase (OHS question, missing info)
    #   2. Web-search and cite the source (non-OHS general question)
    #   3. State an honest answer for trivial/factual questions
    # Anything else (e.g. a hallucinated answer with no grounding) is
    # non-compliant.
    # ALSO: if the model actually used a web search tool this turn,
    # accept its response unconditionally — the user asked for it and
    # the model did it. Forcing a "I don't have that in my reference
    # material" refusal on top of a successful web-search is exactly
    # what caused the user's bug report (post-processor contradicting
    # the model's actual action).
    if web_search_used:
        return GroundingCheck(
            compliant=True,
            confidence=confidence,
            retrieval_status="ok_no_answer",
        )
    if has_refusal(text):
        return GroundingCheck(
            compliant=True,
            confidence=confidence,
            retrieval_status="ok_no_answer",
        )
    if has_web_source(text):
        return GroundingCheck(
            compliant=True,
            confidence=confidence,
            retrieval_status="ok_no_answer",
        )
    log.warning(
        "GROUNDING FAILURE: KB returned no confident results but model did not "
        "refuse OR cite a web source. Forcing canonical refusal. response_len=%d",
        len(text),
    )
    return GroundingCheck(
        compliant=False,
        issue="kb_no_answer_but_no_refusal_or_web_source",
        corrected=CANONICAL_REFUSAL,
        confidence=confidence,
        retrieval_status="ok_no_answer",
    )


def _build_cited_answer(original: str, retrieval_result) -> str:
    """Construct a citation-grounded answer from the retrieved chunks.

    Strategy: keep the model's original prose, append a clearly-marked
    citation-grounded supplement that quotes the top retrieved chunk with
    its citation marker. The user sees both the model's attempt and the
    KB-verified answer.
    """
    chunks = list(getattr(retrieval_result, "chunks", []) or [])
    if not chunks:
        return original

    lines: list[str] = []
    if original.strip():
        lines.append(original.rstrip())
        lines.append("")
        lines.append("--- *corrected from knowledge base* ---")
        lines.append("")

    for i, c in enumerate(chunks[:3], start=1):
        cit = getattr(c, "citation", {}) or {}
        path = cit.get("source_path", "")
        title = cit.get("title") or Path(path).stem if path else ""
        section = cit.get("section", "")
        where = f"`{path}`" if path else "the knowledge base"
        if section:
            where += f" — {section}"
        # Strip the YAML frontmatter from the chunk text so the user sees
        # only the actual content.
        text = getattr(c, "text", "")
        if "---" in text:
            text = text.split("---", 1)[-1].strip()
        if len(text) > 2000:
            text = text[:2000].rsplit(" ", 1)[0] + "…"
        lines.append(f"[citation: {i}] ({where})")
        lines.append(text)
        lines.append("")

    lines.append(CANONICAL_REFUSAL if not original.strip()
                 else "If anything above doesn't answer your question fully, "
                      "let me know and I'll route to support.")
    return "\n".join(lines).strip()


# -----------------------------------------------------------------------------
# KB health preflight
# -----------------------------------------------------------------------------


@dataclass
class HealthStatus:
    healthy: bool
    sources_indexed: int
    chroma_items: int
    bm25_exists: bool
    issues: list[str]


def check_kb_health() -> HealthStatus:
    """Lightweight health check. Called before chat starts.

    Returns a HealthStatus. If unhealthy, callers should warn the user
    or refuse to answer company-fact questions.
    """
    issues: list[str] = []
    sources_indexed = 0
    chroma_items = 0
    bm25_exists = False
    try:
        # SQLite connection (with check_same_thread=False, safe here)
        all_sources = meta.list_all_sources()
        sources_indexed = sum(
            1 for s in all_sources if s.get("status") == "indexed"
        )
        if sources_indexed == 0:
            issues.append("no sources indexed")
    except Exception as e:
        issues.append(f"meta DB error: {e}")

    try:
        from . import indexer
        col = indexer.get_chroma_collection()
        chroma_items = col.count()
        if chroma_items == 0:
            issues.append("chromadb collection empty")
    except Exception as e:
        issues.append(f"chromadb error: {e}")

    try:
        bm25_exists = config.BM25_PATH.exists()
        if not bm25_exists:
            issues.append("bm25 index missing")
    except Exception:
        issues.append("bm25 path check failed")

    return HealthStatus(
        healthy=not issues,
        sources_indexed=sources_indexed,
        chroma_items=chroma_items,
        bm25_exists=bm25_exists,
        issues=issues,
    )
