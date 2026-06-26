"""
Google Cloud Text-to-Speech engine — the reliable, upgradeable option.

Enabled automatically when credentials are present (env var or Streamlit secret).
Supports REAL SSML, so the style presets produce genuine prosody here.

Credentials, in priority order:
  1. GOOGLE_APPLICATION_CREDENTIALS  -> path to a service-account JSON file
  2. GOOGLE_TTS_CREDENTIALS_JSON     -> the service-account JSON as a string
"""

from __future__ import annotations

import asyncio
import json
import os

from tts.config import GOOGLE_VOICES
from tts.engines.base import TTSEngine
from tts.engines.prosody import google_ssml


def _credentials_present() -> bool:
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if path and os.path.isfile(path):
        return True
    return bool(os.environ.get("GOOGLE_TTS_CREDENTIALS_JSON"))


def _make_client():
    from google.cloud import texttospeech

    inline = os.environ.get("GOOGLE_TTS_CREDENTIALS_JSON")
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if (not path or not os.path.isfile(path)) and inline:
        from google.oauth2 import service_account

        info = json.loads(inline)
        creds = service_account.Credentials.from_service_account_info(info)
        return texttospeech.TextToSpeechClient(credentials=creds)
    # Falls back to GOOGLE_APPLICATION_CREDENTIALS / ADC.
    return texttospeech.TextToSpeechClient()


class GoogleTTSEngine(TTSEngine):
    name = "google"

    def __init__(self):
        self._client = None

    @classmethod
    def available(cls) -> bool:
        try:
            import google.cloud.texttospeech  # noqa: F401
        except ImportError:
            return False
        return _credentials_present()

    @property
    def default_voice(self) -> str:
        return GOOGLE_VOICES[0]

    def voices(self) -> list[str]:
        return GOOGLE_VOICES

    @staticmethod
    def _language_code(voice: str) -> str:
        parts = voice.split("-")
        return "-".join(parts[:2]) if len(parts) >= 2 else "en-US"

    async def synthesize(self, text: str, voice: str, style: str) -> bytes:
        voice = voice or self.default_voice
        ssml = google_ssml(text, style, voice)
        return await asyncio.to_thread(self._synthesize_sync, ssml, voice)

    def _synthesize_sync(self, ssml: str, voice: str) -> bytes:
        from google.cloud import texttospeech

        if self._client is None:
            self._client = _make_client()

        response = self._client.synthesize_speech(
            input=texttospeech.SynthesisInput(ssml=ssml),
            voice=texttospeech.VoiceSelectionParams(
                language_code=self._language_code(voice),
                name=voice,
            ),
            audio_config=texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            ),
        )
        return response.audio_content
