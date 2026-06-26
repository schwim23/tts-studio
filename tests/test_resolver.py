import pytest

from tts.inputs.resolver import detect_type, is_url, is_youtube, resolve_input


@pytest.mark.parametrize(
    "src,expected",
    [
        ("https://youtube.com/watch?v=abc", "youtube"),
        ("https://youtu.be/abcDEF12345", "youtube"),
        ("https://www.youtube.com/shorts/xxxxxxxxxxx", "youtube"),
        ("https://example.com/post", "web"),
        ("report.pdf", "pdf"),
        ("notes.docx", "docx"),
        ("readme.md", "textfile"),
        ("notes.txt", "textfile"),
        ("just some raw text", "text"),
    ],
)
def test_detect_type(src, expected):
    assert detect_type(src) == expected


def test_is_youtube_only_true_for_youtube():
    # Guards against the classic `"a" or "b" in s` always-true bug.
    assert is_youtube("https://youtu.be/x")
    assert is_youtube("https://www.youtube.com/watch?v=x")
    assert not is_youtube("https://example.com/video")
    assert not is_youtube("plain text")


def test_is_url():
    assert is_url("http://x.com")
    assert is_url("https://x.com")
    assert not is_url("ftp://x.com")
    assert not is_url("x.com")


def test_resolve_raw_text_passthrough():
    assert resolve_input("hello world") == "hello world"


def test_resolve_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        resolve_input("/no/such/file.pdf")


def test_resolve_empty_raises():
    with pytest.raises(ValueError):
        resolve_input("   ")
