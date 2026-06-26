"""
Translate a semantic style preset into engine-native prosody controls.

IMPORTANT: edge-tts does NOT interpret SSML — if you pass it `<speak>` markup it
reads the tags out loud. So for edge we return rate/pitch/volume KWARGS (verified
to work). For SSML-capable engines (Google) we emit real SSML.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from tts.config import get_preset
from tts.textutils import split_paragraphs, split_sentences, xml_escape

# Approximate Hz shift per semitone (edge-tts pitch is an absolute Hz offset).
_HZ_PER_SEMITONE = 12

# Light, conservative emphasis triggers (SSML engines only).
_EMPHASIS_PATTERNS = [
    re.compile(r"\bkey\s+\w+", re.I),
    re.compile(r"\bmost important\b", re.I),
    re.compile(r"\bcritical\w*", re.I),
    re.compile(r"\bessential\w*", re.I),
    re.compile(r"\bnever\b", re.I),
    re.compile(r"\balways\b", re.I),
]


def edge_kwargs(style: str) -> dict[str, str]:
    """Return rate/pitch/volume kwargs for edge_tts.Communicate."""
    p = get_preset(style)
    hz = int(round(p["pitch_semitones"] * _HZ_PER_SEMITONE))
    return {
        "rate": f"{p['rate_pct']:+d}%",
        "pitch": f"{hz:+d}Hz",
        "volume": "+0%",
    }


def google_ssml(text: str, style: str, voice: str | None = None) -> str:
    """Build valid SSML for Google Cloud TTS from plain text + a style preset."""
    p = get_preset(style)
    rate = f"{100 + p['rate_pct']}%"
    pitch = f"{p['pitch_semitones']:+d}st"
    sent_break = p["sentence_pause_ms"]
    para_break = p["paragraph_pause_ms"]
    emphasis = p["emphasis"]

    paragraphs = split_paragraphs(text) or [text.strip()]
    rendered_paras = []
    for para in paragraphs:
        sentences = split_sentences(para) or [para]
        pieces = []
        for s in sentences:
            esc = xml_escape(s)
            if emphasis != "none":
                esc = _emphasize(esc, emphasis)
            if sent_break:
                esc = f'{esc}<break time="{sent_break}ms"/>'
            pieces.append(esc)
        rendered_paras.append(" ".join(pieces))

    body = f'<break time="{para_break}ms"/>'.join(rendered_paras)
    ssml = (
        '<speak>'
        f'<prosody rate="{rate}" pitch="{pitch}">{body}</prosody>'
        '</speak>'
    )
    return _validate(ssml, text)


def _emphasize(escaped_sentence: str, level: str) -> str:
    """Wrap the first matching key phrase in <emphasis> (max one per sentence)."""
    for pat in _EMPHASIS_PATTERNS:
        m = pat.search(escaped_sentence)
        if m:
            word = m.group(0)
            return escaped_sentence.replace(
                word, f'<emphasis level="{level}">{word}</emphasis>', 1
            )
    return escaped_sentence


def _validate(ssml: str, original: str) -> str:
    """Guarantee the SSML parses; fall back to a plain escaped wrap if not."""
    try:
        ET.fromstring(ssml)
        return ssml
    except ET.ParseError:
        return f"<speak>{xml_escape(original)}</speak>"
