"""Small shared text helpers (sentence/paragraph splitting, XML escaping)."""

from __future__ import annotations

import re

_ABBREV = r"\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|vs|etc|i\.e|e\.g|Inc|Ltd|Co)\."
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def split_sentences(text: str) -> list[str]:
    """Split into sentences, protecting common abbreviations from false breaks."""
    protected = re.sub(_ABBREV, lambda m: m.group(0).replace(".", "<DOT>"), text)
    parts = _SENTENCE_SPLIT.split(protected)
    return [p.replace("<DOT>", ".").strip() for p in parts if p.strip()]


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
