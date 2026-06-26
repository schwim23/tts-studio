"""PDF text extraction via PyMuPDF."""

from __future__ import annotations

from pathlib import Path


def extract_pdf(path: str | Path) -> str:
    import pymupdf  # PyMuPDF

    doc = pymupdf.open(str(path))
    try:
        pages = [page.get_text() for page in doc]
    finally:
        doc.close()
    text = "\n\n".join(p.strip() for p in pages if p.strip())
    if not text.strip():
        raise ValueError("No extractable text found in PDF (it may be scanned images).")
    return text
