import pytest

from tts.inputs.youtube import extract_youtube, video_id


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/abcdefghijk", "abcdefghijk"),
        ("https://www.youtube.com/embed/abcdefghijk", "abcdefghijk"),
    ],
)
def test_video_id_extraction(url, expected):
    assert video_id(url) == expected


def test_video_id_invalid():
    with pytest.raises(ValueError):
        video_id("https://example.com/not-a-video")


@pytest.mark.network
def test_extract_youtube_live():
    # A long-standing video that has captions. May fail if YouTube blocks the IP.
    text = extract_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert len(text) > 50
