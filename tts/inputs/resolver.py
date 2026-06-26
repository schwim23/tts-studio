"""
Resolve any supported source into plain text.

Supported: raw text, .txt/.md files, .pdf, .docx, web URLs, YouTube URLs.
Detection is deterministic (no LLM) — URL scheme, then file extension, else
treat the input as raw text.
"""

from __future__ import annotations

from pathlib import Path

from tts.inputs.docx import extract_docx
from tts.inputs.pdf import extract_pdf
from tts.inputs.web import extract_web
from tts.inputs.youtube import extract_youtube

FILE_EXTS = {".txt", ".md", ".pdf", ".docx"}


def is_url(source: str) -> bool:
    s = source.strip().lower()
    return s.startswith("http://") or s.startswith("https://")


def is_youtube(source: str) -> bool:
    s = source.lower()
    return "youtube.com" in s or "youtu.be" in s


def detect_type(source: str) -> str:
    """Return one of: youtube, web, pdf, docx, textfile, text."""
    if is_url(source):
        return "youtube" if is_youtube(source) else "web"
    suffix = Path(source).suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".docx":
        return "docx"
    if suffix in (".txt", ".md"):
        return "textfile"
    return "text"


def resolve_input(source: str) -> str:
    """Detect the source type and return extracted plain text."""
    source = source.strip()
    if not source:
        raise ValueError("Empty input.")

    kind = detect_type(source)

    if kind == "youtube":
        return extract_youtube(source)
    if kind == "web":
        return extract_web(source)

    if kind in ("pdf", "docx", "textfile"):
        path = Path(source).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {source}")
        if kind == "pdf":
            return extract_pdf(path)
        if kind == "docx":
            return extract_docx(path)
        return path.read_text(encoding="utf-8", errors="replace")

    # Raw text passed directly.
    return source
