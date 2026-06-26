"""Extractor tests against generated fixtures (.txt/.md/.pdf/.docx)."""

from tts.inputs.docx import extract_docx
from tts.inputs.pdf import extract_pdf
from tts.inputs.resolver import resolve_input


def test_pdf_extraction(fixtures):
    text = extract_pdf(fixtures["pdf"])
    assert "key idea" in text
    assert "API" in text


def test_docx_extraction(fixtures):
    text = extract_docx(fixtures["docx"])
    assert "key idea" in text
    assert "Never ignore" in text


def test_textfile_via_resolver(fixtures):
    text = resolve_input(str(fixtures["txt"]))
    assert "Future of Audio" in text


def test_markdown_via_resolver(fixtures):
    text = resolve_input(str(fixtures["md"]))
    assert "key idea" in text


def test_all_fixtures_nonempty(fixtures):
    for kind, path in fixtures.items():
        assert path.stat().st_size > 0, f"{kind} fixture is empty"
