"""
Normalize text before synthesis: strip markdown noise, fix whitespace, and
expand a few acronyms that TTS engines mangle (e.g. "API" -> "A P I").
Paragraph breaks (blank lines) are preserved because prosody uses them.
"""

from __future__ import annotations

import re

# Acronyms commonly mispronounced; spell them out letter-by-letter.
_ACRONYMS = {
    "API": "A P I",
    "URL": "U R L",
    "CPU": "C P U",
    "GPU": "G P U",
    "SQL": "S Q L",
    "HTML": "H T M L",
    "CSS": "C S S",
    "JSON": "Jason",
    "AWS": "A W S",
    "CLI": "C L I",
    "PDF": "P D F",
    "TTS": "T T S",
}


def _expand_acronyms(text: str) -> str:
    for acr, spoken in _ACRONYMS.items():
        text = re.sub(rf"\b{acr}\b", spoken, text)
    return text


def clean_text(text: str, expand_acronyms: bool = True) -> str:
    # Strip markdown emphasis/heading/link syntax but keep the words.
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)          # images
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)      # links -> link text
    text = re.sub(r"`{1,3}([^`]*)`{1,3}", r"\1", text)        # inline/code fences
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)  # headings
    text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)   # bold/italic
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)    # blockquotes

    # Drop bare URLs that survived extraction.
    text = re.sub(r"https?://\S+", "", text)

    if expand_acronyms:
        text = _expand_acronyms(text)

    # Collapse intra-line whitespace, but preserve paragraph (blank-line) breaks.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)

    return text.strip()
