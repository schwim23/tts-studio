"""
Central configuration: voices, style presets, and limits.

Style presets are defined *semantically* (relative rate / pitch / pause feel)
in one place. Each engine translates them into its own native controls:
  - edge-tts  -> rate/pitch/volume kwargs on Communicate (it does NOT honor SSML)
  - Google    -> real SSML (<prosody>, <break>, <emphasis>)
"""

from __future__ import annotations

import os

DEFAULT_ENGINE = "edge"
DEFAULT_STYLE = "conversational"

# Keep chunks comfortably under Google's 5000-byte/request SSML limit and under
# edge-tts's practical reliability ceiling. Split happens on sentence boundaries.
MAX_CHUNK_CHARS = 2500

# Hard cap on accepted input (protects public deployments from huge jobs).
MAX_INPUT_CHARS = int(os.environ.get("TTS_MAX_INPUT_CHARS", "50000"))

# Silence inserted between merged chunks (ms).
CHUNK_GAP_MS = 250

# ---------------------------------------------------------------------------
# Voices
# ---------------------------------------------------------------------------

EDGE_VOICES = [
    "en-US-JennyNeural",
    "en-US-AriaNeural",
    "en-US-GuyNeural",
    "en-US-ChristopherNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "en-AU-NatashaNeural",
    "en-IE-EmilyNeural",
]

GOOGLE_VOICES = [
    "en-US-Neural2-F",
    "en-US-Neural2-J",
    "en-US-Neural2-C",
    "en-US-Neural2-D",
    "en-GB-Neural2-A",
    "en-GB-Neural2-B",
    "en-AU-Neural2-A",
]

# ---------------------------------------------------------------------------
# Style presets (semantic)
# ---------------------------------------------------------------------------
# rate_pct      : percentage offset from default speaking rate (-/+)
# pitch_semitones: pitch shift in semitones (-/+)
# sentence_pause_ms / paragraph_pause_ms: pause lengths
# emphasis      : "none" | "moderate" | "strong" (used by SSML-capable engines)

STYLE_PRESETS: dict[str, dict] = {
    "conversational": {
        "rate_pct": 0,
        "pitch_semitones": 0,
        "sentence_pause_ms": 150,
        "paragraph_pause_ms": 450,
        "emphasis": "moderate",
    },
    "podcast": {
        "rate_pct": -5,
        "pitch_semitones": 0,
        "sentence_pause_ms": 200,
        "paragraph_pause_ms": 550,
        "emphasis": "moderate",
    },
    "documentary": {
        "rate_pct": -10,
        "pitch_semitones": -1,
        "sentence_pause_ms": 250,
        "paragraph_pause_ms": 700,
        "emphasis": "strong",
    },
    "neutral": {
        "rate_pct": 0,
        "pitch_semitones": 0,
        "sentence_pause_ms": 0,
        "paragraph_pause_ms": 300,
        "emphasis": "none",
    },
}

STYLES = list(STYLE_PRESETS.keys())


def get_preset(style: str) -> dict:
    return STYLE_PRESETS.get(style, STYLE_PRESETS[DEFAULT_STYLE])
