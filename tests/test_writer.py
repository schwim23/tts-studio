import pytest

from tts.audio.writer import merge_audio, save_audio


def test_merge_single_chunk_passthrough():
    assert merge_audio([b"abc123"]) == b"abc123"


def test_merge_empty_raises():
    with pytest.raises(ValueError):
        merge_audio([])


def test_merge_drops_empty_blobs():
    # Two non-empty fake blobs fall back to byte-concat (not real mp3).
    assert merge_audio([b"", b"x", b""]) == b"x"


def test_save_audio_writes_file(tmp_path):
    path = save_audio(b"data", tmp_path, "my title")
    assert path.exists()
    assert path.read_bytes() == b"data"
    assert path.suffix == ".mp3"


def test_save_audio_sanitizes_title(tmp_path):
    path = save_audio(b"data", tmp_path, "a/b:c d")
    assert "/" not in path.name
    assert path.name.endswith(".mp3")


def test_save_audio_blank_title_defaults(tmp_path):
    path = save_audio(b"data", tmp_path, "")
    assert path.name == "output.mp3"
