"""Transcribe audio to plain text using mlx-whisper."""

import traceback
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"


def transcribe(
    audio_path: str,
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """Transcribe an audio file to plain text.

    Args:
        audio_path: Path to the audio file.
        model: Model identifier for mlx-whisper.

    Returns:
        Dict with keys: success, transcript, transcript_file, error.
    """
    result = {
        "success": False,
        "transcript": None,
        "transcript_file": None,
        "error": None,
    }

    audio_file = Path(audio_path)
    if not audio_file.exists():
        result["error"] = f"Audio file not found: {audio_path}"
        return result

    transcript_file = audio_file.with_suffix(".txt")

    try:
        import mlx_whisper

        transcription = mlx_whisper.transcribe(
            str(audio_file),
            path_or_hf_repo=model,
            verbose=False,
            word_timestamps=False,
        )

        text = transcription.get("text", "").strip()

        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(text)

        result["transcript"] = text
        result["transcript_file"] = str(transcript_file.resolve())
        result["success"] = True

    except ImportError:
        result["error"] = (
            "mlx-whisper is not installed. Run: uv pip install mlx-whisper"
        )
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["traceback"] = traceback.format_exc()

    return result
