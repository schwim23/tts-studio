#!/usr/bin/env python3
"""
TTS Studio — command-line interface.

Examples:
  python cli.py "Hello world"
  python cli.py article.pdf --title my-article --style podcast
  python cli.py https://example.com/post --title post
  python cli.py https://youtu.be/VIDEOID --title talk
  python cli.py notes.docx --engine google --voice en-US-Neural2-J
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from tts.config import DEFAULT_ENGINE, DEFAULT_STYLE, STYLES
from tts.engines.factory import available_engines
from tts.pipeline import synthesize_to_file


def _progress(done: int, total: int) -> None:
    print(f"      synthesizing chunk {done}/{total}...", end="\r", flush=True)


async def _run(args: argparse.Namespace) -> int:
    print(f"[1/2] Resolving + preparing: {args.source[:70]}")
    try:
        path = await synthesize_to_file(
            args.source,
            args.title,
            engine_name=args.engine,
            voice=args.voice,
            style=args.style,
            output_dir=args.output_dir,
            on_progress=_progress,
        )
    except Exception as e:  # noqa: BLE001 - surface a clean message to the user
        print(f"\n❌ {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"\n[2/2] ✅ Saved: {path}")
    return 0


def main() -> None:
    engines = available_engines()
    parser = argparse.ArgumentParser(
        description="Convert text, files, or URLs to narrated audio.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("source", help="Raw text, a file path, or a URL")
    parser.add_argument("--title", default="output", help="Output filename (no extension)")
    parser.add_argument(
        "--engine",
        default=DEFAULT_ENGINE,
        choices=engines,
        help=f"TTS engine. Available now: {engines}",
    )
    parser.add_argument("--voice", default=None, help="Voice id (engine default if omitted)")
    parser.add_argument(
        "--style", default=DEFAULT_STYLE, choices=STYLES, help="Prosody style preset"
    )
    parser.add_argument(
        "--output-dir", default="~/audio_output", help="Where to save the MP3"
    )
    args = parser.parse_args()
    raise SystemExit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
