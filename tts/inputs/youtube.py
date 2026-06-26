"""YouTube transcript extraction. (Note: YouTube also rate-limits datacenter IPs.)"""

from __future__ import annotations

import re

_ID_PATTERNS = [
    re.compile(r"(?:v=)([A-Za-z0-9_-]{11})"),
    re.compile(r"youtu\.be/([A-Za-z0-9_-]{11})"),
    re.compile(r"youtube\.com/(?:embed|shorts)/([A-Za-z0-9_-]{11})"),
]


def video_id(url: str) -> str:
    for pat in _ID_PATTERNS:
        m = pat.search(url)
        if m:
            return m.group(1)
    raise ValueError(f"Could not find a YouTube video id in '{url}'.")


def extract_youtube(url: str) -> str:
    from youtube_transcript_api import YouTubeTranscriptApi

    vid = video_id(url)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid)
    except Exception as e:  # noqa: BLE001 - library raises many subclasses
        raise ValueError(f"Could not fetch transcript for video '{vid}': {e}") from e
    text = " ".join(chunk["text"] for chunk in transcript if chunk.get("text"))
    if not text.strip():
        raise ValueError(f"Transcript for '{vid}' was empty.")
    return text
