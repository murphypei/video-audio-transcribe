"""Extract audio from local video files using ffmpeg."""

import subprocess
from pathlib import Path
from typing import Any

from vat.utils import sanitize_filename


def extract_audio(
    video_path: str,
    output_dir: Path,
    audio_format: str = "mp3",
    output_filename: str | None = None,
) -> dict[str, Any]:
    """Extract audio from a local video file using ffmpeg.

    Returns:
        Dict with keys: success, input_file, output_file, error.
    """
    video_file = Path(video_path).resolve()
    if not video_file.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not video_file.is_file():
        raise ValueError(f"Path is not a file: {video_path}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = sanitize_filename(output_filename) if output_filename else video_file.stem
    ext = audio_format.lower()
    output_file = output_dir / f"{stem}.{ext}"

    result = {
        "success": False,
        "source": "local",
        "input_file": str(video_file),
        "output_file": None,
        "error": None,
    }

    cmd = ["ffmpeg", "-y", "-i", str(video_file), "-vn"]

    if ext == "mp3":
        cmd.extend(
            [
                "-ar", "44100",
                "-ac", "2",
                "-b:a", "192k",
                "-codec:a", "libmp3lame",
                str(output_file),
            ]
        )
    elif ext == "wav":
        cmd.extend(
            [
                "-ar", "44100",
                "-ac", "2",
                "-codec:a", "pcm_s16le",
                str(output_file),
            ]
        )
    else:
        raise ValueError(f"Unsupported audio format: {audio_format}. Use 'mp3' or 'wav'.")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        result["output_file"] = str(output_file.resolve())
        result["success"] = True
    except subprocess.CalledProcessError as e:
        result["error"] = f"ffmpeg failed: {e.stderr}"
    except FileNotFoundError:
        result["error"] = "ffmpeg not found. Please install ffmpeg and ensure it's in PATH."

    return result
