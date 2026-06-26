"""
Edge TTS engine — free Microsoft neural voices, no API key.

Prosody is applied via rate/pitch/volume KWARGS (edge-tts does not honor SSML).
Heads-up: edge-tts talks to a Microsoft endpoint that may rate-limit datacenter
IPs, so on cloud hosts it can intermittently fail — that's when the Google
upgrade engine earns its keep.
"""

from __future__ import annotations

import edge_tts

from tts.config import EDGE_VOICES
from tts.engines.base import TTSEngine
from tts.engines.prosody import edge_kwargs


class EdgeError(RuntimeError):
    """Raised when edge-tts fails (often a cloud-IP rate limit / block)."""


class EdgeTTSEngine(TTSEngine):
    name = "edge"

    @property
    def default_voice(self) -> str:
        return EDGE_VOICES[0]

    def voices(self) -> list[str]:
        return EDGE_VOICES

    async def synthesize(self, text: str, voice: str, style: str) -> bytes:
        voice = voice or self.default_voice
        kwargs = edge_kwargs(style)
        communicate = edge_tts.Communicate(text, voice, **kwargs)

        audio = bytearray()
        try:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio.extend(chunk["data"])
        except Exception as e:  # noqa: BLE001 - normalize to a typed error
            raise EdgeError(
                "edge-tts request failed. On cloud hosts this is usually an IP "
                "rate-limit/block — add a Google key to use the Google engine."
            ) from e

        if not audio:
            raise EdgeError("edge-tts returned no audio (possible rate-limit/block).")
        return bytes(audio)
