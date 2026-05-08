"""Shared utilities."""

import re
from pathlib import Path
from urllib.parse import urlparse


ILLEGAL_CHARS = re.compile(r'[\\/:*?"<>|]')


def sanitize_filename(name: str, max_len: int = 120) -> str:
    """Remove illegal filename characters and truncate."""
    name = ILLEGAL_CHARS.sub("_", name)
    name = name.strip(" .")
    if len(name) > max_len:
        name = name[:max_len]
    return name or "untitled"


def detect_source(input_path: str) -> str:
    """Return 'youtube', 'bilibili', or 'local'."""
    p = Path(input_path)
    if p.exists() and p.is_file():
        return "local"

    parsed = urlparse(input_path)
    domain = parsed.netloc.lower()

    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    if "bilibili.com" in domain:
        return "bilibili"

    if not p.exists():
        raise ValueError(
            f"Input is neither a valid local file nor a recognized URL: {input_path}"
        )

    return "local"
