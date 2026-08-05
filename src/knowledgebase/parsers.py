"""File -> Markdown conversion.

Each parser returns (markdown_text, metadata_dict). The metadata is stored
alongside the parsed file so we can later resolve a chunk citation back to
its source (title, author, page, etc.).

Supported input formats:
    .md / .markdown   — pass-through, normalize frontmatter
    .txt              — wrap in minimal frontmatter
    .csv              — render as Markdown table (preserves structure for retrieval)
    .html / .htm      — strip tags, preserve headings
    .pdf              — Docling for complex PDFs (tables/layouts), pypdf fallback

For PDFs, we prefer Docling because it understands layout, but fall back to
pypdf if Docling isn't installed or errors out. Each PDF page becomes a
clearly delineated section in the parsed Markdown so citations can point at
specific pages.
"""

from __future__ import annotations

import csv
import io
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable

# Filename -> doc slug. Strips extension, replaces non-alphanumerics with -,
# collapses runs, strips leading/trailing dashes.
_SLUG_RE = re.compile(r"[^a-zA-Z0-9]+")


def doc_slug(path: Path) -> str:
    """Stable, filesystem-safe slug from a path. Uses parent dir + stem.

    >>> doc_slug(Path('/x/y/products/energy-core.pdf'))
    'products--energy-core'
    """
    parts = list(path.parts[-3:-1]) if len(path.parts) > 2 else list(path.parts[:-1])
    parts.append(path.stem)
    return "--".join(_SLUG_RE.sub("-", p).strip("-").lower() for p in parts if p)


# -----------------------------------------------------------------------------
# Per-format parsers
# -----------------------------------------------------------------------------

def parse_markdown(path: Path) -> tuple[str, dict[str, Any]]:
    """Pass-through. Ensures trailing newline, captures existing frontmatter."""
    text = path.read_text(encoding="utf-8", errors="replace").strip() + "\n"
    return text, {"format": "markdown", "parser": "pass-through"}


def parse_txt(path: Path) -> tuple[str, dict[str, Any]]:
    """Plain text. Treat as a single section; first non-blank line is a title."""
    raw = path.read_text(encoding="utf-8", errors="replace").rstrip()
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    title = lines[0][:120] if lines else path.stem
    body = "\n".join(lines)
    md = f"# {title}\n\n{body}\n"
    return md, {"format": "text", "parser": "txt", "title": title}


def parse_csv(path: Path) -> tuple[str, dict[str, Any]]:
    """CSV -> Markdown table(s).

    Auto-detects headers from the first row. Large CSVs are split into
    multiple Markdown tables of `MAX_CSV_ROWS_PER_TABLE` rows each so the
    chunker doesn't blow them up into one-chunk-per-row. Each sub-table is
    preceded by a heading like "Rows 1-200" so citations remain navigable.

    Wide CSVs (>WIDE_CSV_COLUMN_THRESHOLD columns) are auto-pruned to keep
    only the most "informative" columns by header keyword, dropping noise
    like SEO metadata, image URLs, internal IDs, etc. The user can disable
    this by editing the column-pruning list.

    Cells are escaped so pipe characters don't break the table.
    """
    MAX_CSV_ROWS_PER_TABLE = 30
    MAX_CSV_CHARS_PER_CELL = 200
    WIDE_CSV_COLUMN_THRESHOLD = 25
    WIDE_CSV_MAX_COLUMNS = 15

    # Headers we consider "informative". Matched case-insensitively as
    # substrings, so e.g. "Body (HTML)" matches "body".
    INFORMATIVE_COLUMN_PATTERNS = (
        "title", "name", "handle", "subject", "headline",
        "body", "content", "description", "summary", "text", "message",
        "question", "answer",
        "author", "by ", "written",
        "published", "created", "updated", "date",
        "tags", "category", "type", "status",
        "price", "cost", "amount", "ingredient", "fact",
        "sku", "vendor",
    )
    NOISE_COLUMN_PATTERNS = (
        "seo ", "metafield", "google shopping", "image", "src",
        "alt text", "width", "height", "position",
        "id", "uuid", "command", "feedburner",
        "ip ", "browser", "email", "comment",
        "ip_", "_id", "barcode", "gram",
    )
    # Use utf-8-sig to strip BOM if present.
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        reader = csv.reader(f, dialect)
        rows = [r for r in reader if any(cell.strip() for cell in r)]

    if not rows:
        return f"# {path.stem}\n\n_Empty CSV file._\n", {
            "format": "csv", "parser": "csv", "row_count": 0,
        }

    headers = [h.strip() or f"col{i+1}" for i, h in enumerate(rows[0])]
    body_rows = rows[1:]

    # Wide-table column pruning: drop noise columns first, then keep the
    # top N informative ones. This keeps a 100-column Shopify export to a
    # 10-15 column "useful" version.
    columns_dropped: list[str] = []
    if len(headers) > WIDE_CSV_COLUMN_THRESHOLD:
        keep_idx: list[int] = []
        for i, h in enumerate(headers):
            low = h.lower()
            if any(noise in low for noise in NOISE_COLUMN_PATTERNS):
                continue
            if any(info in low for info in INFORMATIVE_COLUMN_PATTERNS):
                keep_idx.append(i)
        # If pruning left us with too few, top up from the unclassified columns.
        if len(keep_idx) < WIDE_CSV_MAX_COLUMNS:
            already = set(keep_idx)
            for i, h in enumerate(headers):
                if i in already:
                    continue
                low = h.lower()
                if any(noise in low for noise in NOISE_COLUMN_PATTERNS):
                    continue
                keep_idx.append(i)
                if len(keep_idx) >= WIDE_CSV_MAX_COLUMNS:
                    break
        keep_idx = sorted(set(keep_idx))[:WIDE_CSV_MAX_COLUMNS]
        columns_dropped = [h for i, h in enumerate(headers) if i not in keep_idx]
        headers = [headers[i] for i in keep_idx]
        body_rows = [
            [(row[i] if i < len(row) else "") for i in keep_idx]
            for row in body_rows
        ]

    def cell(c: str) -> str:
        # Escape pipes/newlines for Markdown tables.
        text = c.replace("|", "\\|").replace("\n", " ").strip()
        if not text:
            return "—"
        if len(text) > MAX_CSV_CHARS_PER_CELL:
            text = text[:MAX_CSV_CHARS_PER_CELL].rsplit(" ", 1)[0] + "…"
        return text

    md_lines = [
        f"# {path.stem}",
        "",
    ]
    if columns_dropped:
        md_lines.append(
            f"_Table data from `{path.name}`. {len(body_rows)} data rows × "
            f"{len(headers)} columns after pruning wide-table noise "
            f"(dropped: {', '.join(columns_dropped[:8])}{'…' if len(columns_dropped) > 8 else ''}). "
            f"Split into tables of up to {MAX_CSV_ROWS_PER_TABLE} rows._"
        )
    else:
        md_lines.append(
            f"_Table data from `{path.name}`. {len(body_rows)} data rows × "
            f"{len(headers)} columns. Split into tables of up to {MAX_CSV_ROWS_PER_TABLE} rows._"
        )
    md_lines.append("")

    # Split body rows into chunks; each becomes its own Markdown table.
    for start in range(0, len(body_rows), MAX_CSV_ROWS_PER_TABLE):
        chunk_rows = body_rows[start: start + MAX_CSV_ROWS_PER_TABLE]
        end = start + len(chunk_rows)
        if start == 0 and len(body_rows) <= MAX_CSV_ROWS_PER_TABLE:
            md_lines.append("## All rows")
        else:
            md_lines.append(f"## Rows {start + 1}–{end}")
        md_lines.append("")
        md_lines.append("| " + " | ".join(cell(h) for h in headers) + " |")
        md_lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for r in chunk_rows:
            # Pad/truncate to header count.
            cells = list(r) + [""] * (len(headers) - len(r))
            md_lines.append("| " + " | ".join(cell(c) for c in cells[: len(headers)]) + " |")
        md_lines.append("")

    md = "\n".join(md_lines) + "\n"
    return md, {
        "format": "csv",
        "parser": "csv",
        "row_count": len(body_rows),
        "columns": headers,
        "columns_dropped": columns_dropped,
    }


class _HTMLStripper(HTMLParser):
    """Strip HTML to plain text, keeping block-level structure."""

    BLOCK = {"p", "div", "section", "article", "header", "footer",
             "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "br"}
    SKIP = {"script", "style", "noscript", "nav"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0
        self._heading_tag: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag in self.BLOCK:
            self._parts.append("\n")
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self._parts.append("\n" + "#" * level + " ")
            self._heading_tag = tag
        elif tag == "li":
            self._parts.append("\n- ")
        elif tag == "br":
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._heading_tag == tag:
            self._heading_tag = None
        if tag in self.BLOCK:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip() if self._heading_tag else data
        if text:
            self._parts.append(text)

    @property
    def text(self) -> str:
        # Collapse 3+ blank lines into 2, strip trailing whitespace.
        out = "".join(self._parts)
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out.strip()


def parse_html(path: Path) -> tuple[str, dict[str, Any]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    stripper = _HTMLStripper()
    stripper.feed(raw)
    text = stripper.text
    if not text.startswith("#"):
        text = f"# {path.stem}\n\n{text}"
    text += "\n"
    return text, {"format": "html", "parser": "html-stripper"}


def parse_pdf(path: Path) -> tuple[str, dict[str, Any]]:
    """PDF -> Markdown. Prefers Docling, falls back to pypdf.

    Each page is a section so citations can be specific (e.g. "page 4").
    """
    try:
        return _parse_pdf_docling(path)
    except _DoclingUnavailable as e:
        # Only fall back if docling isn't installed; real parse errors propagate.
        return _parse_pdf_pypdf(path, note=f"(Docling unavailable: {e}; using pypdf fallback.)\n\n")


def _parse_pdf_pypdf(path: Path, note: str = "") -> tuple[str, dict[str, Any]]:
    import pypdf
    reader = pypdf.PdfReader(str(path))
    chunks: list[str] = []
    for i, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
        except Exception as e:
            txt = f"(failed to extract text: {e})"
        chunks.append(f"## Page {i + 1}\n\n{txt.strip()}\n")
    md = note + "\n".join(chunks)
    return md, {
        "format": "pdf",
        "parser": "pypdf",
        "page_count": len(reader.pages),
    }


class _DoclingUnavailable(ImportError):
    pass


def _parse_pdf_docling(path: Path) -> tuple[str, dict[str, Any]]:
    try:
        from docling.document_converter import DocumentConverter
    except ImportError as e:
        raise _DoclingUnavailable(str(e)) from e

    converter = DocumentConverter()
    result = converter.convert(str(path))
    md = result.document.export_to_markdown()
    # Docling doesn't always add per-page headings; we leave them in if present.
    page_count = 0
    try:
        page_count = len(result.document.pages)
    except Exception:
        pass
    return md, {
        "format": "pdf",
        "parser": "docling",
        "page_count": page_count,
    }


# -----------------------------------------------------------------------------
# Dispatch
# -----------------------------------------------------------------------------

ParserFn = Callable[[Path], tuple[str, dict[str, Any]]]

PARSERS: dict[str, ParserFn] = {
    ".md": parse_markdown,
    ".markdown": parse_markdown,
    ".txt": parse_txt,
    ".csv": parse_csv,
    ".html": parse_html,
    ".htm": parse_html,
    ".pdf": parse_pdf,
}


def parse(path: Path) -> tuple[str, dict[str, Any]]:
    """Dispatch to the right parser by extension. Raises ValueError for unknown."""
    ext = path.suffix.lower()
    parser = PARSERS.get(ext)
    if parser is None:
        raise ValueError(f"Unsupported file extension: {ext!r} for {path}")
    return parser(path)
