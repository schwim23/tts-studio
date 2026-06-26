"""
YouTube transcript extraction (youtube-transcript-api >= 1.0).

The 1.x API is instance-based: `YouTubeTranscriptApi().fetch(id)` returns a
FetchedTranscript of snippets (the old classmethod `get_transcript` was removed).
Note: YouTube also rate-limits/blocks datacenter IPs, so this can fail on cloud
hosts even for videos that have captions.
"""

from __future__ import annotations

import re

_ID_PATTERNS = [
    re.compile(r"(?:v=)([A-Za-z0-9_-]{11})"),
    re.compile(r"youtu\.be/([A-Za-z0-9_-]{11})"),
    re.compile(r"youtube\.com/(?:embed|shorts)/([A-Za-z0-9_-]{11})"),
]

_PREFERRED_LANGS = ["en", "en-US", "en-GB"]


def video_id(url: str) -> str:
    for pat in _ID_PATTERNS:
        m = pat.search(url)
        if m:
            return m.group(1)
    raise ValueError(f"Could not find a YouTube video id in '{url}'.")


def _snippets_to_text(fetched) -> str:
    # FetchedTranscript is iterable of snippet objects with a `.text` attr;
    # fall back to the raw-dict form for older/edge builds.
    try:
        parts = [s.text for s in fetched if getattr(s, "text", "").strip()]
    except TypeError:
        parts = [d["text"] for d in fetched if d.get("text", "").strip()]
    return " ".join(parts)


def extract_youtube(url: str) -> str:
    from youtube_transcript_api import YouTubeTranscriptApi

    vid = video_id(url)
    api = YouTubeTranscriptApi()

    try:
        fetched = api.fetch(vid, languages=_PREFERRED_LANGS)
    except Exception:
        # No preferred-language transcript — fall back to whatever exists
        # (manually created first, then auto-generated, in any language).
        try:
            transcript_list = api.list(vid)
            transcript = next(iter(transcript_list))
            fetched = transcript.fetch()
        except Exception as e:  # noqa: BLE001 - many subclasses; normalize
            raise ValueError(
                f"Could not fetch a transcript for video '{vid}'. It may have "
                f"captions disabled, or YouTube is blocking this IP. ({e})"
            ) from e

    text = _snippets_to_text(fetched)
    if not text.strip():
        raise ValueError(f"Transcript for '{vid}' was empty.")
    return text
