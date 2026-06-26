"""Word (.docx) text extraction via python-docx."""

from __future__ import annotations

from pathlib import Path


def extract_docx(path: str | Path) -> str:
    from docx import Document

    doc = Document(str(path))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    text = "\n\n".join(paragraphs)
    if not text.strip():
        raise ValueError("No text found in the Word document.")
    return text
