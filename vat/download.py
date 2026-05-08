"""Download audio from YouTube / Bilibili using yt-dlp."""

import traceback
from pathlib import Path
from typing import Any

from vat.utils import detect_source, sanitize_filename


def _build_ytdlp_options(
    output_dir: Path,
    audio_format: str,
    output_filename: str | None = None,
    source: str = "youtube",
    use_cookies: bool = True,
) -> dict[str, Any]:
    """Build yt-dlp options for audio extraction."""
    ydl_opts: dict[str, Any] = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
    }

    if use_cookies:
        ydl_opts["cookiesfrombrowser"] = ("chrome", None, None, None)

    if output_filename:
        template = str(output_dir / f"{sanitize_filename(output_filename)}.%(ext)s")
    else:
        template = str(output_dir / "%(title)s.%(ext)s")
    ydl_opts["outtmpl"] = template

    if audio_format.lower() == "mp3":
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
    elif audio_format.lower() == "wav":
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": None,
            }
        ]
        ydl_opts["postprocessor_args"] = {
            "FFmpegExtractAudio": ["-ar", "44100", "ac", "2"]
        }
    else:
        raise ValueError(f"Unsupported audio format: {audio_format}. Use 'mp3' or 'wav'.")

    if source == "youtube":
        ydl_opts["extractor_args"] = {
            "youtube": {"player_client": ["android", "tv_embedded", "tv", "ios"]},
        }

    return ydl_opts


def _find_output_file(output_dir: Path, stem: str, ext: str) -> Path | None:
    """Find the downloaded audio file."""
    candidates = list(output_dir.glob(f"{stem}*.{ext}"))
    if not candidates:
        candidates = sorted(
            output_dir.glob(f"*.{ext}"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    return candidates[0] if candidates else None


def _download(
    url: str,
    output_dir: Path,
    audio_format: str,
    output_filename: str | None,
    source: str,
    use_cookies: bool,
) -> tuple[bool, str | None, str | None]:
    """Try download once. Returns (success, output_file, error)."""
    try:
        import yt_dlp

        ydl_opts = _build_ytdlp_options(
            output_dir, audio_format, output_filename, source, use_cookies
        )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return False, None, "Failed to extract video information"

            title = info.get("title", "Unknown")
            ydl.download([url])

        expected_ext = audio_format.lower()
        stem = sanitize_filename(output_filename) if output_filename else sanitize_filename(title)
        output_file = _find_output_file(output_dir, stem, expected_ext)

        if output_file:
            return True, str(output_file.resolve()), None
        else:
            return False, None, "Download completed but output file not found"

    except Exception as e:
        return False, None, f"{type(e).__name__}: {str(e)}"


def download_audio(
    url: str,
    output_dir: Path,
    audio_format: str = "mp3",
    output_filename: str | None = None,
) -> dict[str, Any]:
    """Download and extract audio from a YouTube or Bilibili URL.

    Returns:
        Dict with keys: success, output_file, title, duration, error.
    """
    source = detect_source(url)
    if source == "local":
        raise ValueError(f"Expected URL but got local file path: {url}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "success": False,
        "source": source,
        "url": url,
        "output_file": None,
        "title": None,
        "duration": None,
        "error": None,
    }

    try:
        import yt_dlp

        # Step 1: Extract metadata (always try with cookies first)
        info_opts = {"quiet": True}
        if source == "bilibili":
            info_opts["cookiesfrombrowser"] = ("chrome", None, None, None)

        if source == "youtube":
            info_opts["extractor_args"] = {
                "youtube": {"player_client": ["android", "tv_embedded", "tv", "ios"]},
            }

        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise Exception("Failed to extract video information")
            result["title"] = info.get("title", "Unknown")
            result["duration"] = info.get("duration")

        # Step 2: Download audio
        # YouTube: try without cookies first (player_client fallback usually works),
        # then fallback to cookies if needed.
        # Bilibili: always use cookies for best audio quality.
        if source == "youtube":
            success, output_file, error = _download(
                url, output_dir, audio_format, output_filename, source, use_cookies=False
            )
            if not success and "cookie" in (error or "").lower():
                success, output_file, error = _download(
                    url, output_dir, audio_format, output_filename, source, use_cookies=True
                )
        else:
            success, output_file, error = _download(
                url, output_dir, audio_format, output_filename, source, use_cookies=True
            )

        if success:
            result["output_file"] = output_file
            result["success"] = True
        else:
            result["error"] = error

    except ImportError:
        result["error"] = "yt-dlp is not installed. Run: uv pip install yt-dlp"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        result["traceback"] = traceback.format_exc()

    return result
