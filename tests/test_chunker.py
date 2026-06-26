from tts.processors.chunker import chunk_text


def test_short_text_single_chunk():
    assert chunk_text("Just one short sentence.") == ["Just one short sentence."]


def test_empty_text():
    assert chunk_text("") == []


def test_long_text_splits_under_limit():
    text = " ".join(f"Sentence number {i} here." for i in range(200))
    chunks = chunk_text(text, max_chars=200)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)
    assert all(c.strip() for c in chunks)


def test_oversized_single_sentence_hard_split():
    giant = "word " * 500  # one ~2500-char "sentence" with no terminators
    chunks = chunk_text(giant, max_chars=100)
    assert all(len(c) <= 100 for c in chunks)
    assert len(chunks) > 1


def test_no_content_lost():
    text = "Alpha sentence. Beta sentence. Gamma sentence. Delta sentence."
    chunks = chunk_text(text, max_chars=25)
    joined = " ".join(chunks)
    for word in ("Alpha", "Beta", "Gamma", "Delta"):
        assert word in joined
