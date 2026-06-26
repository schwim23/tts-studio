# 🎙️ TTS Studio

Turn **text, PDFs, Word docs, web articles, and YouTube videos** into narrated
audio — from a web UI or the command line.

- **Keyless by default.** Runs out of the box on free [edge-tts](https://github.com/rany2/edge-tts) (Microsoft neural voices). No account, no API key.
- **One-key upgrade.** Drop in a Google Cloud key and a reliable, full-prosody [Google Cloud TTS](https://cloud.google.com/text-to-speech) engine appears automatically — no code change.
- **Style presets** (`conversational`, `podcast`, `documentary`, `neutral`) that actually change the delivery.
- Web UI (Streamlit) **and** a CLI, sharing one pipeline.

> **Why two engines?** edge-tts is free and excellent locally, but it talks to a
> Microsoft endpoint that **rate-limits datacenter IPs** — so on a cloud host it
> can intermittently fail. Google Cloud TTS is an official API (no IP blocking),
> has a **perpetual free tier** (~1M Neural chars/month), and supports real SSML.
> Use edge for free/local; flip to Google for a rock-solid hosted demo.

---

## Quick start (zero config)

```bash
git clone https://github.com/schwim23/tts-studio.git
cd tts-studio
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# ffmpeg is required for merging multi-chunk audio:
#   macOS:  brew install ffmpeg
#   Ubuntu: sudo apt install ffmpeg

# CLI
python cli.py "Hello, this is TTS Studio." --title hello

# Web UI
streamlit run app.py
```

That's it — no API key needed.

---

## Usage

### CLI

```bash
python cli.py SOURCE [--title NAME] [--engine edge|google]
                     [--voice VOICE] [--style STYLE] [--output-dir DIR]
```

`SOURCE` is auto-detected: raw text, a file path (`.txt` `.md` `.pdf` `.docx`),
a web URL, or a YouTube URL.

```bash
python cli.py article.pdf --title my-article --style podcast
python cli.py https://example.com/post --title post
python cli.py https://youtu.be/VIDEOID --title talk
python cli.py notes.docx --engine google --voice en-US-Neural2-J
```

Audio is written to `~/audio_output/<title>.mp3` by default.

### Web UI

```bash
streamlit run app.py
```

Three input tabs (Text / File / URL), voice + style pickers, inline playback,
and a download button. The engine dropdown shows `google` only when a key is
configured.

---

## Styles

Styles are defined **semantically** in `tts/config.py` and translated per engine
(rate/pitch kwargs for edge, real SSML for Google):

| Style | Feel |
|---|---|
| `conversational` | Warm, natural pacing (default) |
| `podcast` | Clear, slightly slower, deliberate |
| `documentary` | Measured, authoritative, dramatic pauses + emphasis |
| `neutral` | Minimal styling, plain delivery |

> **Note on edge-tts + SSML:** edge-tts does **not** interpret SSML — passing it
> `<speak>` markup makes it read the tags aloud. TTS Studio therefore applies
> prosody to edge via `rate`/`pitch`/`volume` parameters, and reserves real SSML
> for Google. (This was verified empirically; see `tts/engines/prosody.py`.)

---

## Upgrading to Google Cloud TTS

1. In Google Cloud: enable the **Text-to-Speech API**, create a **service
   account**, and download its **JSON key**.
2. Make the key available — the app auto-detects it:

   **Local (file path):**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   ```

   **Local or cloud (inline JSON):**
   ```bash
   export GOOGLE_TTS_CREDENTIALS_JSON='{"type":"service_account", ...}'
   ```

3. `google` now appears in the CLI `--engine` choices and the UI dropdown.
   `edge` remains the default; nothing else changes.

See `.env.example` for all optional variables.

---

## Deploy the live web version (Streamlit Community Cloud)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → pick the
   repo → main file **`app.py`** → Deploy.
   - `requirements.txt` and `packages.txt` (which installs **ffmpeg**) are picked
     up automatically.
3. **(Recommended)** For a reliable demo that won't hit edge-tts rate limits,
   add your Google key under **App → Settings → Secrets**:
   ```toml
   GOOGLE_TTS_CREDENTIALS_JSON = '''
   {"type": "service_account", "project_id": "...", ...}
   '''
   ```
   The app reads secrets into the environment at startup and the Google engine
   activates with **no redeploy or code change**.

> Running keyless on the cloud is fine for light use, but expect occasional
> edge-tts failures on shared cloud IPs — that's exactly what the Google key
> fixes.

---

## Architecture

A deterministic pipeline (not an agent — there are no decisions to make):

```
source ─▶ resolve ─▶ clean ─▶ chunk ─▶ synthesize ─▶ merge ─▶ MP3
         (inputs/)  (cleaner) (chunker) (engine)    (audio/)
```

```
tts/
├── config.py            # voices, style presets, limits
├── pipeline.py          # orchestrates the whole flow
├── runtime.py           # bridges Streamlit secrets -> env
├── textutils.py         # sentence/paragraph split, XML escape
├── inputs/
│   ├── resolver.py      # detect source type + dispatch
│   ├── safety.py        # SSRF guard for URLs
│   ├── web.py · pdf.py · docx.py · youtube.py
├── processors/
│   ├── cleaner.py       # strip markdown, expand acronyms
│   └── chunker.py       # sentence-boundary splitting
├── engines/
│   ├── base.py          # engine interface (returns MP3 bytes)
│   ├── edge.py          # free, keyless (rate/pitch prosody)
│   ├── google.py        # reliable upgrade (real SSML)
│   ├── prosody.py       # style preset -> engine-native controls
│   └── factory.py       # credential-driven engine selection
└── audio/writer.py      # merge chunks (pydub/ffmpeg) + save

app.py    # Streamlit UI
cli.py    # command-line interface
```

**Design choices worth knowing:**
- Engines return **bytes**, so the UI never juggles temp files and merging is trivial.
- The factory is **credential-driven** — the upgrade path is literally "a key exists".
- Public URLs are fetched behind an **SSRF guard** (`tts/inputs/safety.py`) that
  blocks private/loopback/link-local IPs and the cloud metadata endpoint.
- Input is capped at `TTS_MAX_INPUT_CHARS` (default 50,000) to protect public deploys.

---

## Testing

The suite is split into **offline unit tests** (gating) and **live network tests**
(opt-in, non-gating), because edge-tts/YouTube rate-limit datacenter IPs.

```bash
pip install -r requirements-dev.txt

pytest                    # offline unit tests (fast, no network)
pytest --run-network      # also run live edge-tts / web tests
ruff check .              # lint
```

**Fixtures.** `tests/fixtures/generate.py` programmatically creates real sample
`.txt`, `.md`, `.pdf`, and `.docx` files with known content, so extractor tests run
against genuine documents (not mocks). It's used automatically by the test
suite and is runnable standalone for demos:

```bash
python tests/fixtures/generate.py ./samples
```

**Coverage highlights:**

| Area | What's verified |
|---|---|
| `resolver` | type detection, the `is_youtube` correctness, missing-file errors |
| `inputs` | real PDF/DOCX/TXT/MD extraction via generated fixtures |
| `cleaner` | acronym expansion, markdown stripping, paragraph preservation |
| `chunker` | size limits, hard-split of oversized sentences, no content loss |
| `prosody` | edge kwargs format; Google SSML is valid XML; emphasis rules |
| `safety` | SSRF guard blocks metadata/loopback/private IPs and bad schemes |
| `factory` | edge always present; google appears with credentials |
| `writer` | merge passthrough, filename sanitization |
| `network` *(opt-in)* | live edge-tts synthesis + full pipeline |

**CI** (`.github/workflows/ci.yml`) runs lint + offline tests on Python 3.10 and
3.12 (with ffmpeg installed) as the gating job, and the live network tests as a
separate **non-blocking** job.

---

## License

MIT.
