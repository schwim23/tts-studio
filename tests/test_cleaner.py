from tts.processors.cleaner import clean_text


def test_acronyms_expanded():
    assert "A P I" in clean_text("The API is fast.")
    assert "U R L" in clean_text("Open the URL now.")


def test_markdown_stripped():
    out = clean_text("# Heading\n\n**bold** and *italic* and `code`")
    assert "#" not in out
    assert "*" not in out
    assert "`" not in out
    assert "bold" in out and "italic" in out and "code" in out


def test_links_become_text():
    out = clean_text("See [the docs](https://example.com) now")
    assert "the docs" in out
    assert "example.com" not in out


def test_bare_urls_removed():
    out = clean_text("Visit https://example.com/page for more")
    assert "http" not in out


def test_paragraph_breaks_preserved():
    out = clean_text("First para.\n\nSecond para.")
    assert "\n\n" in out


def test_whitespace_collapsed():
    assert clean_text("too    many     spaces") == "too many spaces"
