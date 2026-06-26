"""
Merge per-chunk MP3 bytes into a single audio file.

Prefers pydub + ffmpeg (clean joins with a short silence gap). Falls back to raw
byte concatenation if pydub/ffmpeg is unavailable — playable for MP3, just less
tidy at the seams.
"""

from __future__ import annotations

from pathlib import Path

from tts.config import CHUNK_GAP_MS


def merge_audio(chunks: list[bytes], gap_ms: int = CHUNK_GAP_MS) -> bytes:
    """Merge a list of MP3 byte blobs into one MP3 blob."""
    chunks = [c for c in chunks if c]
    if not chunks:
        raise ValueError("No audio to merge.")
    if len(chunks) == 1:
        return chunks[0]

    try:
        return _merge_pydub(chunks, gap_ms)
    except Exception:  # noqa: BLE001 - fall back if pydub/ffmpeg missing
        return b"".join(chunks)


def _merge_pydub(chunks: list[bytes], gap_ms: int) -> bytes:
    import io

    from pydub import AudioSegment

    combined = AudioSegment.empty()
    gap = AudioSegment.silent(duration=gap_ms)
    for i, blob in enumerate(chunks):
        seg = AudioSegment.from_file(io.BytesIO(blob), format="mp3")
        if i:
            combined += gap
        combined += seg

    out = io.BytesIO()
    combined.export(out, format="mp3")
    return out.getvalue()


def save_audio(data: bytes, output_dir: str | Path, title: str) -> Path:
    """Write MP3 bytes to <output_dir>/<safe-title>.mp3 and return the path."""
    out_dir = Path(output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in title).strip("_")
    safe = safe or "output"
    path = out_dir / f"{safe}.mp3"
    path.write_bytes(data)
    return path
