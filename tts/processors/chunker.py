"""
Split cleaned text into synthesis-safe chunks at sentence boundaries.

Keeps each chunk under MAX_CHUNK_CHARS (Google's per-request SSML limit is
5000 bytes; we stay well under). A single oversized sentence is hard-split.
"""

from __future__ import annotations

from tts.config import MAX_CHUNK_CHARS
from tts.textutils import split_paragraphs, split_sentences


def chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    current = ""

    def flush():
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    for para in split_paragraphs(text):
        for sentence in split_sentences(para):
            # Hard-split a single sentence that's too long on its own.
            while len(sentence) > max_chars:
                flush()
                chunks.append(sentence[:max_chars])
                sentence = sentence[max_chars:]
            if len(current) + len(sentence) + 1 > max_chars:
                flush()
            current = f"{current} {sentence}".strip()
        # Paragraph boundary: prefer to start a new chunk if we're getting full.
        if len(current) > max_chars * 0.8:
            flush()

    flush()
    return chunks
