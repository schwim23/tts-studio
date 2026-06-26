"""Engine interface. Engines return MP3 BYTES for one chunk of text."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TTSEngine(ABC):
    #: short identifier used by the factory / UI (e.g. "edge", "google")
    name: str = "base"

    @property
    @abstractmethod
    def default_voice(self) -> str: ...

    @abstractmethod
    def voices(self) -> list[str]:
        """List of selectable voice ids for this engine."""

    @abstractmethod
    async def synthesize(self, text: str, voice: str, style: str) -> bytes:
        """Synthesize one chunk of text and return MP3 bytes."""

    @classmethod
    def available(cls) -> bool:
        """Whether this engine can run right now (library importable + creds)."""
        return True
