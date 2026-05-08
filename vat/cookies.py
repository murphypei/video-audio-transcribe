"""Cookie management: export from Chrome to local file, load for downloads."""

from pathlib import Path
from typing import Any

DEFAULT_COOKIE_FILE = Path.home() / ".config" / "vat" / "cookies.txt"


def _build_cookie_dir() -> Path:
    """Ensure cookie directory exists."""
    cookie_dir = Path.home() / ".config" / "vat"
    cookie_dir.mkdir(parents=True, exist_ok=True)
    return cookie_dir


def export_cookies(
    output_file: str | None = None,
    browser: str = "chrome",
) -> dict[str, Any]:
    """Export cookies from browser to a local Netscape-format file.

    This allows subsequent downloads to use the saved cookies without
    requiring the browser to be open.

    Args:
        output_file: Path to save cookies. Defaults to ~/.config/vat/cookies.txt
        browser: Browser to extract from (chrome, safari, firefox, edge).

    Returns:
        Dict with success, output_file, cookie_count, error.
    """
    result = {
        "success": False,
        "output_file": None,
        "cookie_count": 0,
        "error": None,
    }

    out_path = Path(output_file) if output_file else DEFAULT_COOKIE_FILE
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Use yt-dlp CLI for reliable cookie export; the Python API does not
        # guarantee flushing the cookie jar when extraction fails.
        import subprocess

        cmd = [
            "yt-dlp",
            "--quiet",
            "--no-warnings",
            "--skip-download",
            "--cookies-from-browser",
            browser,
            "--cookies",
            str(out_path),
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        ]
        subprocess.run(cmd, capture_output=True, check=False)

        if out_path.exists():
            # Count non-comment lines
            with open(out_path, "r", encoding="utf-8") as f:
                lines = [ln for ln in f if ln.strip() and not ln.startswith("#")]
            result["cookie_count"] = len(lines)
            result["output_file"] = str(out_path.resolve())
            result["success"] = True
        else:
            result["error"] = "Cookie export completed but file was not created"

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"

    return result


def get_cookie_options(
    cookie_file: str | None = None,
    browser: str = "chrome",
) -> dict[str, Any]:
    """Build yt-dlp cookie options.

    Priority:
    1. Explicitly provided cookie_file
    2. Default local cookie file (~/.config/vat/cookies.txt) if exists
    3. Live browser extraction as fallback

    Returns:
        Dict to merge into yt-dlp options.
    """
    opts: dict[str, Any] = {}

    # Priority 1: explicit file
    if cookie_file:
        p = Path(cookie_file)
        if p.exists():
            opts["cookies"] = str(p.resolve())
            return opts

    # Priority 2: default local file
    if DEFAULT_COOKIE_FILE.exists():
        opts["cookies"] = str(DEFAULT_COOKIE_FILE.resolve())
        return opts

    # Priority 3: live browser
    opts["cookiesfrombrowser"] = (browser, None, None, None)
    return opts
