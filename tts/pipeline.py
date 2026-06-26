"""
Orchestrates the full flow: resolve -> clean -> chunk -> synthesize -> merge.

`synthesize_to_bytes` returns the merged MP3 in memory (used by the Streamlit UI);
`synthesize_to_file` also writes it to disk (used by the CLI). An optional
`on_progress(done, total)` callback drives progress bars.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from tts.audio.writer import merge_audio, save_audio
from tts.config import DEFAULT_ENGINE, DEFAULT_STYLE, MAX_INPUT_CHARS
from tts.engines.factory import get_engine
from tts.inputs.resolver import resolve_input
from tts.processors.chunker import chunk_text
from tts.processors.cleaner import clean_text

ProgressCb = Callable[[int, int], None]


def prepare_text(source: str) -> tuple[str, list[str]]:
    """Resolve + clean + chunk. Returns (cleaned_text, chunks). Enforces size cap."""
    raw = resolve_input(source)
    if len(raw) > MAX_INPUT_CHARS:
        raise ValueError(
            f"Input is {len(raw):,} characters, over the {MAX_INPUT_CHARS:,} limit. "
            "Shorten it or raise TTS_MAX_INPUT_CHARS."
        )
    cleaned = clean_text(raw)
    chunks = chunk_text(cleaned)
    if not chunks:
        raise ValueError("Nothing to synthesize after cleaning.")
    return cleaned, chunks


async def synthesize_to_bytes(
    source: str,
    *,
    engine_name: str = DEFAULT_ENGINE,
    voice: str | None = None,
    style: str = DEFAULT_STYLE,
    on_progress: ProgressCb | None = None,
) -> bytes:
    engine = get_engine(engine_name)
    voice = voice or engine.default_voice

    _, chunks = prepare_text(source)
    total = len(chunks)
    rendered: list[bytes] = []
    for i, chunk in enumerate(chunks):
        rendered.append(await engine.synthesize(chunk, voice, style))
        if on_progress:
            on_progress(i + 1, total)

    return merge_audio(rendered)


async def synthesize_to_file(
    source: str,
    title: str,
    *,
    engine_name: str = DEFAULT_ENGINE,
    voice: str | None = None,
    style: str = DEFAULT_STYLE,
    output_dir: str | Path = "~/audio_output",
    on_progress: ProgressCb | None = None,
) -> Path:
    audio = await synthesize_to_bytes(
        source,
        engine_name=engine_name,
        voice=voice,
        style=style,
        on_progress=on_progress,
    )
    return save_audio(audio, output_dir, title)
