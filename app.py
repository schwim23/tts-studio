"""
TTS Studio — Streamlit UI.   Run:  streamlit run app.py

Keyless by default (edge-tts). If a Google Cloud key is present (env var locally,
or pasted into Streamlit secrets), the Google engine appears automatically.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import streamlit as st

# Bring hosting secrets into the environment BEFORE engines are inspected.
from tts.runtime import load_secrets_into_env

try:
    load_secrets_into_env(st.secrets)
except Exception:  # noqa: BLE001 - no secrets file is fine
    pass

from tts.config import STYLES  # noqa: E402
from tts.engines.edge import EdgeError  # noqa: E402
from tts.engines.factory import available_engines, get_engine  # noqa: E402
from tts.pipeline import synthesize_to_bytes  # noqa: E402

st.set_page_config(page_title="TTS Studio", page_icon="🎙️", layout="centered")

st.title("🎙️ TTS Studio")
st.caption("Turn text, PDFs, Word docs, web articles, and YouTube videos into audio.")

ENGINES = available_engines()
STYLE_HELP = {
    "conversational": "Warm, natural pacing.",
    "podcast": "Clear, slightly slower, deliberate.",
    "documentary": "Measured, authoritative, dramatic pauses.",
    "neutral": "Minimal styling — plain delivery.",
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    engine_name = st.selectbox(
        "Engine",
        ENGINES,
        index=0,
        help="edge = free, no key. google = reliable + real prosody (needs a key).",
    )
    engine = get_engine(engine_name)
    voice = st.selectbox("Voice", engine.voices(), index=0)
    style = st.selectbox("Style", STYLES, index=0, help="Prosody preset.")
    st.caption(STYLE_HELP.get(style, ""))

    st.divider()
    if "google" in ENGINES:
        st.success("Google engine active — reliable & full SSML prosody.")
    else:
        st.info(
            "Running keyless on **edge-tts**. To unlock the reliable Google engine, "
            "add a `GOOGLE_TTS_CREDENTIALS_JSON` secret — no redeploy needed.",
            icon="🔑",
        )

# ---------------------------------------------------------------------------
# Input tabs
# ---------------------------------------------------------------------------
tab_text, tab_file, tab_url = st.tabs(["📝 Text", "📄 File", "🔗 URL"])
source: str | None = None
default_title = "output"

with tab_text:
    raw = st.text_area("Paste text", height=240, placeholder="Type or paste anything…")
    if raw.strip():
        source, default_title = raw.strip(), "text"

with tab_file:
    up = st.file_uploader("Upload", type=["pdf", "txt", "md", "docx"])
    if up is not None:
        suffix = Path(up.name).suffix
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(up.read())
        tmp.close()
        source, default_title = tmp.name, Path(up.name).stem
        st.success(f"Loaded {up.name}")

with tab_url:
    url = st.text_input("Article or YouTube URL", placeholder="https://…")
    if url.strip():
        source, default_title = url.strip(), "web"

st.divider()
c1, c2 = st.columns([3, 1])
title = c1.text_input("Filename", value=default_title, label_visibility="collapsed")
go = c2.button("🎙️ Generate", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if go:
    if not source:
        st.warning("Add some text, upload a file, or paste a URL first.")
        st.stop()

    progress = st.progress(0.0, text="Starting…")

    def _on_progress(done: int, total: int) -> None:
        progress.progress(done / total, text=f"Synthesizing chunk {done}/{total}…")

    try:
        audio = asyncio.run(
            synthesize_to_bytes(
                source,
                engine_name=engine_name,
                voice=voice,
                style=style,
                on_progress=_on_progress,
            )
        )
        progress.progress(1.0, text="Done")
        st.audio(audio, format="audio/mp3")
        st.download_button(
            "⬇️ Download MP3",
            data=audio,
            file_name=f"{title or 'output'}.mp3",
            mime="audio/mpeg",
            use_container_width=True,
        )
    except EdgeError as e:
        progress.empty()
        st.error(
            f"{e}\n\nThis is common on cloud hosts. Add a Google key to switch to the "
            "reliable Google engine.",
            icon="⚠️",
        )
    except Exception as e:  # noqa: BLE001 - show a friendly message
        progress.empty()
        st.error(f"{type(e).__name__}: {e}")
    finally:
        # Clean up an uploaded temp file if we made one.
        if source and source.startswith(tempfile.gettempdir()):
            try:
                Path(source).unlink(missing_ok=True)
            except OSError:
                pass
