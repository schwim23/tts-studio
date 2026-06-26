"""
Live tests — only run with `pytest --run-network`. These hit Microsoft's
edge-tts endpoint, which may rate-limit datacenter IPs (so they're opt-in and
non-gating in CI).
"""

import pytest

from tts.engines.edge import EdgeTTSEngine
from tts.pipeline import synthesize_to_bytes

pytestmark = pytest.mark.network


async def test_edge_synthesize_returns_mp3():
    engine = EdgeTTSEngine()
    audio = await engine.synthesize("Hello from a test.", engine.default_voice, "neutral")
    assert isinstance(audio, bytes)
    assert len(audio) > 1000


async def test_full_pipeline_raw_text():
    audio = await synthesize_to_bytes(
        "First sentence. Second sentence. Third sentence.",
        style="podcast",
    )
    assert len(audio) > 1000
