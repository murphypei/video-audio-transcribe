"""End-to-end pipeline: download/extract audio then transcribe."""

from pathlib import Path
from typing import Any

from vat.download import download_audio
from vat.extract import extract_audio
from vat.transcribe import transcribe
from vat.utils import detect_source


def process(
    input_path: str,
    output_dir: str = "./downloads",
    audio_format: str = "mp3",
    output_filename: str | None = None,
    step: str = "all",
) -> dict[str, Any]:
    """Process a single input through the pipeline.

    Args:
        input_path: URL or local file path.
        output_dir: Directory for outputs.
        audio_format: 'mp3' or 'wav'.
        output_filename: Custom filename stem.
        step: 'all' | 'download' | 'extract' | 'transcribe'.

    Returns:
        Result dict with success, output_file, transcript_file, etc.
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    source = detect_source(input_path)
    result: dict[str, Any] = {
        "success": False,
        "source": source,
        "input": input_path,
        "output_file": None,
        "transcript_file": None,
        "error": None,
    }

    # Step 1: Get audio file
    if step in ("all", "download", "extract"):
        if source in ("youtube", "bilibili"):
            extract_result = download_audio(
                input_path, output_dir_path, audio_format, output_filename
            )
        else:
            extract_result = extract_audio(
                input_path, output_dir_path, audio_format, output_filename
            )

        if not extract_result.get("success"):
            result["error"] = extract_result.get("error")
            return result

        result["output_file"] = extract_result.get("output_file")
        result["title"] = extract_result.get("title")
        result["duration"] = extract_result.get("duration")

        if step in ("download", "extract"):
            result["success"] = True
            return result

    # If step is transcribe only, input_path is the audio file
    audio_file = result["output_file"] or input_path

    # Step 2: Transcribe
    if step in ("all", "transcribe"):
        tx_result = transcribe(audio_file)
        result["transcript"] = tx_result.get("transcript")
        result["transcript_file"] = tx_result.get("transcript_file")

        if not tx_result.get("success"):
            result["error"] = f"Transcription failed: {tx_result.get('error')}"
            return result

    result["success"] = True
    return result
