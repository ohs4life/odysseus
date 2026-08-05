"""Markdown -> chunks with YAML frontmatter.

Chunking strategy: section-aware, target ~512 tokens, 15% overlap.

Algorithm:
  1. Parse Markdown into a stream of (heading_level, heading_text, body_lines).
  2. Walk the stream, accumulating sections. A "section" is one heading + its
     body until the next heading of equal-or-higher level.
  3. If a section fits in one chunk -> emit it as a single chunk.
  4. If a section is too long -> split by paragraph; paragraphs that are still
     too long get split by sentence.
  5. Consecutive chunks from the same section get the small overlap.

The output is one .md file per chunk with a YAML frontmatter describing
provenance (source, section, page, token estimate, content hash). The
frontmatter is what makes the chunks self-describing for the retriever
and for human audits.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from . import config, hash as hashlib
from .parsers import doc_slug

# Matches a Markdown header at start of line, capturing the level and text.
_HEADER_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# Paragraph break: two+ newlines.
_PARA_RE = re.compile(r"\n\s*\n")
# Sentence end: period/question mark/exclamation followed by space + uppercase.
# Conservative; we don't try to be perfect, just to break long paragraphs.
_SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'])")
# Markdown table row: pipe-delimited.
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")

# Tokens-to-chars approximation (English-heavy text).
_TOKENS_TO_CHARS = config.CHARS_PER_TOKEN

# Max table rows per chunk. Tables are extremely dense; a 30-col table with
# 200-char cells hits the chunk limit in just a few rows. We adapt based
# on the number of columns to keep chunks roughly within target size.
def _table_rows_per_chunk(column_count: int) -> int:
    if column_count <= 6:
        return 25
    if column_count <= 12:
        return 15
    if column_count <= 25:
        return 8
    if column_count <= 50:
        return 4
    return 2  # very wide tables (Shopify exports etc.)


def estimate_tokens(text: str) -> int:
    """Crude token estimate: chars / 4. Good enough for chunk sizing."""
    return max(1, len(text) // _TOKENS_TO_CHARS)


# -----------------------------------------------------------------------------
# Section parsing
# -----------------------------------------------------------------------------


def _parse_sections(md_text: str) -> list[dict[str, Any]]:
    """Split Markdown into [{level, heading, body}, ...] preserving order."""
    lines = md_text.splitlines()
    sections: list[dict[str, Any]] = []
    cur_level = 0
    cur_heading = ""
    cur_body: list[str] = []

    def flush() -> None:
        body = "\n".join(cur_body).strip()
        sections.append({
            "level": cur_level,
            "heading": cur_heading.strip(),
            "body": body,
        })

    for line in lines:
        m = _HEADER_RE.match(line)
        if m:
            flush()
            cur_level = len(m.group(1))
            cur_heading = m.group(2)
            cur_body = []
        else:
            cur_body.append(line)
    flush()
    return sections


# -----------------------------------------------------------------------------
# Splitting helpers
# -----------------------------------------------------------------------------


def _split_paragraphs(text: str) -> list[str]:
    """Split text on blank lines. Returns non-empty paragraphs."""
    return [p.strip() for p in _PARA_RE.split(text) if p.strip()]


def _split_long_paragraph(text: str, max_chars: int) -> list[str]:
    """Split a paragraph that's too long into sentences."""
    sentences = _SENT_RE.split(text)
    out: list[str] = []
    buf = ""
    for s in sentences:
        if not buf:
            buf = s
            continue
        if len(buf) + len(s) + 1 > max_chars and buf:
            out.append(buf)
            buf = s
        else:
            buf = buf + " " + s
    if buf:
        out.append(buf)
    return out


def _pack(
    units: list[str], *, max_chars: int, overlap_chars: int,
) -> list[str]:
    """Pack a list of strings into chunks of <= max_chars, with overlap."""
    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0

    def emit() -> None:
        nonlocal buf, buf_len
        if not buf:
            return
        chunks.append("\n\n".join(buf))
        # Overlap: keep the tail of the just-emitted chunk for context.
        tail = chunks[-1]
        if overlap_chars > 0 and len(tail) > overlap_chars:
            overlap_text = tail[-overlap_chars:]
            # Round to start of the last unit to avoid mid-sentence fragments.
            last_break = overlap_text.rfind("\n\n")
            if last_break != -1:
                overlap_text = overlap_text[last_break + 2:]
            buf = [overlap_text]
            buf_len = len(overlap_text)
        else:
            buf = []
            buf_len = 0

    for u in units:
        unit_len = len(u)
        # Single unit bigger than max_chars: hard split.
        if unit_len > max_chars:
            emit()
            for piece in _split_long_paragraph(u, max_chars):
                chunks.append(piece)
            continue
        if buf and buf_len + unit_len + 2 > max_chars:
            emit()
        buf.append(u)
        buf_len += unit_len + 2  # +2 for the "\n\n" joiner

    emit()
    return [c for c in chunks if c.strip()]


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------


def chunk_markdown(
    md_text: str,
    *,
    source_meta: dict[str, Any],
) -> list[dict[str, Any]]:
    """Split a parsed Markdown document into chunk records.

    Each returned record has:
        text:        the chunk text (without frontmatter)
        section:     heading text the chunk belongs to
        chunk_index: 0-based index within the document
        total_chunks: count of chunks produced for this document
        token_estimate: int
        content_hash: sha256 of the chunk text
    """
    target_tokens = int(config.get("chunk_target_tokens"))
    overlap_tokens = int(config.get("chunk_overlap_tokens"))
    min_tokens = int(config.CHUNK_MIN_TOKENS)
    max_chars = target_tokens * _TOKENS_TO_CHARS
    overlap_chars = overlap_tokens * _TOKENS_TO_CHARS

    sections = _parse_sections(md_text)
    chunks_text: list[str] = []
    chunk_sections: list[str] = []

    for sec in sections:
        # Build the section header (e.g., "## Heading") + body.
        if sec["heading"]:
            header = ("#" * max(1, sec["level"])) + " " + sec["heading"]
        else:
            header = ""
        body = sec["body"]
        if not body and not header:
            continue

        # If the section (header + body) is small, emit as one chunk.
        whole = (header + "\n\n" + body).strip() if header else body
        if estimate_tokens(whole) <= target_tokens:
            chunks_text.append(whole)
            chunk_sections.append(sec["heading"] or "(untitled)")
            continue

        # Special-case Markdown tables: split by row batches. Tables are dense;
        # naive paragraph splitting produces one-chunk-per-row which is wrong.
        table_chunks = _split_table(body)
        if table_chunks is not None:
            for sub in table_chunks:
                chunks_text.append(sub)
                chunk_sections.append(sec["heading"] or "(untitled)")
            continue

        # Otherwise split body into paragraphs and pack them.
        units = _split_paragraphs(body)
        if header:
            units.insert(0, header)
        for sub in _pack(units, max_chars=max_chars, overlap_chars=overlap_chars):
            chunks_text.append(sub)
            chunk_sections.append(sec["heading"] or "(untitled)")

    # Drop chunks that are too small (typically overlap tails at the end).
    keep = [
        (t, s) for t, s in zip(chunks_text, chunk_sections)
        if estimate_tokens(t) >= min_tokens
    ]

    total = len(keep)
    out: list[dict[str, Any]] = []
    for i, (text, section) in enumerate(keep):
        out.append({
            "text": text,
            "section": section,
            "chunk_index": i,
            "total_chunks": total,
            "token_estimate": estimate_tokens(text),
            "content_hash": hashlib.sha256_text(text),
        })
    return out


# -----------------------------------------------------------------------------
# Table-aware chunking
# -----------------------------------------------------------------------------


def _is_table(body: str) -> bool:
    """True if the section body is dominated by Markdown table rows."""
    lines = body.splitlines()
    if len(lines) < 3:
        return False
    table_lines = sum(
        1 for ln in lines
        if _TABLE_ROW_RE.match(ln) or _TABLE_SEP_RE.match(ln)
    )
    return table_lines >= 3 and table_lines / len(lines) > 0.5


def _split_table(body: str) -> list[str] | None:
    """Split a table-heavy body into chunks, preserving the header row in each.

    Returns None if the body isn't actually a table.
    Each chunk = header row + separator + up to N data rows, where N adapts
    to the table's column count (wider tables => fewer rows per chunk so the
    chunk stays near the target token size).
    """
    if not _is_table(body):
        return None
    lines = body.splitlines()
    # Find header + separator (typically the first 2 table lines).
    header_idx = None
    sep_idx = None
    for i, ln in enumerate(lines[:5]):
        if _TABLE_SEP_RE.match(ln):
            sep_idx = i
            header_idx = i - 1
            break
    if header_idx is None or sep_idx is None or header_idx < 0:
        return None
    header = lines[header_idx]
    separator = lines[sep_idx]
    data_rows = [
        ln for ln in lines[sep_idx + 1:]
        if ln.strip() and _TABLE_ROW_RE.match(ln)
    ]
    if not data_rows:
        return None
    column_count = max(1, header.count("|") - 1)
    rows_per_chunk = _table_rows_per_chunk(column_count)
    out: list[str] = []
    for start in range(0, len(data_rows), rows_per_chunk):
        batch = data_rows[start: start + rows_per_chunk]
        out.append("\n".join([header, separator, *batch]))
    return out


# -----------------------------------------------------------------------------
# File output
# -----------------------------------------------------------------------------


_FRONTMATTER_TEMPLATE = """---
source_doc: {source_doc}
source_path: {source_path}
source_type: {source_type}
title: {title}
section: {section}
page: {page}
chunk_index: {chunk_index}
total_chunks: {total_chunks}
token_estimate: {token_estimate}
content_hash: {content_hash}
ingested_at: {ingested_at}
parser: {parser}
parser_version: {parser_version}
tags: {tags}
---

{body}
"""


def write_chunk(
    *,
    chunk_dir: Path,
    chunk_index: int,
    text: str,
    source_meta: dict[str, Any],
    section: str,
    total_chunks: int,
    token_estimate: int,
    content_hash: str,
    tags: list[str] | None = None,
) -> Path:
    """Write a single chunk to disk as Markdown with YAML frontmatter.

    Filename: chunk-NNN-{short_hash}.md  (zero-padded index, hash for dedup).
    """
    chunk_dir.mkdir(parents=True, exist_ok=True)
    short = hashlib.short_hash(content_hash, length=8)
    fname = f"chunk-{chunk_index:03d}-{short}.md"
    path = chunk_dir / fname

    ingested_at = source_meta.get("ingested_at", "")
    body = _FRONTMATTER_TEMPLATE.format(
        source_doc=source_meta.get("doc_slug", ""),
        source_path=source_meta.get("rel_path", ""),
        source_type=source_meta.get("format", ""),
        title=_yaml_escape(source_meta.get("title") or source_meta.get("doc_slug", "")),
        section=_yaml_escape(section),
        page=source_meta.get("page", ""),
        chunk_index=chunk_index,
        total_chunks=total_chunks,
        token_estimate=token_estimate,
        content_hash=content_hash,
        ingested_at=ingested_at,
        parser=source_meta.get("parser", ""),
        parser_version=source_meta.get("parser_version", ""),
        tags=yaml.safe_dump(tags or [], default_flow_style=True).strip(),
        body=text,
    )
    path.write_text(body, encoding="utf-8")
    return path


def _yaml_escape(s: str) -> str:
    """Quote a string for safe YAML inclusion (handles special chars)."""
    if not s:
        return '""'
    needs_quote = any(c in s for c in ":#-[]{},&*!|>'\"%@`\n")
    if needs_quote:
        # Use double quotes; escape internal quotes/backslashes.
        escaped = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return s
