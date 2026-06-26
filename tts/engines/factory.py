"""
Credential-driven engine selection.

`edge` is always available (keyless). `google` appears only when a Google key is
present in the environment / Streamlit secrets — this is the entire "upgrade
path": add a key, the engine shows up, no code change.
"""

from __future__ import annotations

from tts.config import DEFAULT_ENGINE
from tts.engines.base import TTSEngine
from tts.engines.edge import EdgeTTSEngine
from tts.engines.google import GoogleTTSEngine

# Order = display/preference order. edge stays the default even when google
# is available, because the user wants keyless-first behavior.
_REGISTRY: list[type[TTSEngine]] = [EdgeTTSEngine, GoogleTTSEngine]


def available_engines() -> list[str]:
    return [e.name for e in _REGISTRY if e.available()]


def get_engine(name: str | None = None) -> TTSEngine:
    name = name or DEFAULT_ENGINE
    for engine_cls in _REGISTRY:
        if engine_cls.name == name:
            if not engine_cls.available():
                raise ValueError(
                    f"Engine '{name}' is not available — missing credentials or library."
                )
            return engine_cls()
    raise ValueError(f"Unknown engine '{name}'. Available: {available_engines()}")
