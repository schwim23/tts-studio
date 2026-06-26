"""
Bridge hosting secrets into environment variables the engines read.

On Streamlit Community Cloud you paste secrets into the app's Secrets UI; this
copies the relevant keys into os.environ so the credential-driven factory picks
them up. Framework-agnostic: pass any mapping (e.g. st.secrets).
"""

from __future__ import annotations

import os
from collections.abc import Mapping

# Secret keys we care about -> env vars they map to (same name here).
_PASSTHROUGH = (
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_TTS_CREDENTIALS_JSON",
    "TTS_MAX_INPUT_CHARS",
)


def load_secrets_into_env(secrets: Mapping) -> None:
    """Copy known secret keys into os.environ if not already set."""
    for key in _PASSTHROUGH:
        if key in os.environ:
            continue
        try:
            value = secrets[key]
        except (KeyError, TypeError):
            continue
        if value:
            os.environ[key] = str(value)
