"""URL -> clean article text via trafilatura (strips nav/ads/boilerplate)."""

from __future__ import annotations

from tts.inputs.safety import assert_safe_url


def extract_web(url: str) -> str:
    import trafilatura

    assert_safe_url(url)  # SSRF guard before any network call

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise ValueError(f"Could not download '{url}'.")
    text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    if not text or not text.strip():
        raise ValueError(
            f"Could not extract readable article text from '{url}' "
            "(may be paywalled or JS-rendered)."
        )
    return text.strip()
