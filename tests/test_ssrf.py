"""SSRF guard tests. Uses IP literals so no DNS/network is needed."""

import pytest

from tts.inputs.safety import UnsafeURLError, assert_safe_url, is_safe_url

BLOCKED = [
    "http://169.254.169.254/latest/meta-data/",  # cloud metadata
    "http://127.0.0.1/",                          # loopback
    "http://10.0.0.5/internal",                   # private
    "http://192.168.1.1/",                        # private
    "file:///etc/passwd",                         # non-http scheme
    "ftp://203.0.113.1/x",                        # non-http scheme
]

ALLOWED = [
    "http://93.184.216.34/",      # public IP literal
    "https://93.184.216.34/page", # public IP literal
]


@pytest.mark.parametrize("url", BLOCKED)
def test_blocked_urls(url):
    assert not is_safe_url(url)
    with pytest.raises(UnsafeURLError):
        assert_safe_url(url)


@pytest.mark.parametrize("url", ALLOWED)
def test_allowed_urls(url):
    assert is_safe_url(url)


def test_no_host():
    assert not is_safe_url("http://")
