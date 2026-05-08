"""CLI entry point."""

import argparse
import json
import sys
from pathlib import Path

from vat.cookies import export_cookies
from vat.pipeline import process


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download audio from URLs or extract from local videos, then transcribe.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline for single URL
  vat "https://www.bilibili.com/video/BV..."

  # Batch processing
  vat url1 url2 url3 --output-dir ./out

  # Local video
  vat /path/to/video.mp4 --output-dir ./audio

  # Only download audio (no transcription)
  vat <url> --step download

  # Only transcribe existing audio file
  vat audio.mp3 --step transcribe
        """,
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        default=[],
        help="One or more URLs (YouTube/Bilibili) or local file paths",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./downloads",
        help="Output directory (default: ./downloads)",
    )
    parser.add_argument(
        "--format",
        choices=["mp3", "wav"],
        default="mp3",
        help="Output audio format (default: mp3)",
    )
    parser.add_argument(
        "--step",
        choices=["all", "download", "extract", "transcribe"],
        default="all",
        help=(
            "Pipeline step to run (default: all). "
            "'download'/'extract' fetches audio only; "
            "'transcribe' expects an existing audio file."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON lines",
    )
    parser.add_argument(
        "--export-cookies",
        action="store_true",
        help="Export Chrome cookies to local file and exit",
    )

    args = parser.parse_args()

    if not args.inputs and not args.export_cookies:
        parser.error("No inputs provided. Use --export-cookies or provide URLs/file paths.")

    if args.export_cookies:
        result = export_cookies()
        if result["success"]:
            print(f"Cookies exported: {result['output_file']} ({result['cookie_count']} cookies)")
            sys.exit(0)
        else:
            print(f"Cookie export failed: {result['error']}", file=sys.stderr)
            sys.exit(1)

    results = []
    any_failed = False

    for inp in args.inputs:
        result = process(
            input_path=inp,
            output_dir=args.output_dir,
            audio_format=args.format,
            step=args.step,
        )
        results.append(result)
        if not result["success"]:
            any_failed = True
            print(f"ERROR: {inp} -> {result['error']}", file=sys.stderr)
        else:
            print(f"OK: {inp}")
            if result.get("output_file"):
                print(f"  Audio: {result['output_file']}")
            if result.get("transcript_file"):
                print(f"  Text:  {result['transcript_file']}")

    if args.json:
        for r in results:
            print(json.dumps(r, ensure_ascii=False))

    sys.exit(1 if any_failed else 0)


if __name__ == "__main__":
    main()
