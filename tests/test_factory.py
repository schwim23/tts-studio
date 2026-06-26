import pytest

from tts.engines.factory import available_engines, get_engine


def test_edge_always_available():
    assert "edge" in available_engines()


def test_default_engine_is_edge():
    assert get_engine().name == "edge"


def test_unknown_engine_raises():
    with pytest.raises(ValueError):
        get_engine("does-not-exist")


def test_google_appears_with_credentials(monkeypatch):
    monkeypatch.setenv("GOOGLE_TTS_CREDENTIALS_JSON", '{"type":"service_account"}')
    assert "google" in available_engines()


def test_google_absent_without_credentials(monkeypatch):
    monkeypatch.delenv("GOOGLE_TTS_CREDENTIALS_JSON", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    assert "google" not in available_engines()
