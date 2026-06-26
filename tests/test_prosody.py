import re
import xml.etree.ElementTree as ET

import pytest

from tts.config import STYLES
from tts.engines.prosody import edge_kwargs, google_ssml


@pytest.mark.parametrize("style", STYLES)
def test_edge_kwargs_format(style):
    kw = edge_kwargs(style)
    assert set(kw) == {"rate", "pitch", "volume"}
    assert re.fullmatch(r"[+-]\d+%", kw["rate"])
    assert re.fullmatch(r"[+-]\d+Hz", kw["pitch"])
    assert re.fullmatch(r"[+-]\d+%", kw["volume"])


@pytest.mark.parametrize("style", STYLES)
def test_google_ssml_is_valid_xml(style):
    ssml = google_ssml("Hello there. Is this working?\n\nNew paragraph.", style)
    root = ET.fromstring(ssml)  # raises if invalid
    assert root.tag == "speak"


def test_google_ssml_has_prosody_and_breaks():
    ssml = google_ssml("First sentence. Second sentence.", "podcast")
    assert "<prosody" in ssml
    assert "<break" in ssml


def test_documentary_adds_emphasis():
    ssml = google_ssml("This is a critical safety point.", "documentary")
    assert "<emphasis" in ssml


def test_neutral_has_no_emphasis():
    ssml = google_ssml("This is a critical safety point.", "neutral")
    assert "<emphasis" not in ssml


def test_ssml_escapes_special_chars():
    ssml = google_ssml("Tom & Jerry <fight> here.", "neutral")
    ET.fromstring(ssml)  # must still parse
    assert "&amp;" in ssml
