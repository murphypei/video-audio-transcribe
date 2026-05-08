"""Simple sanity tests."""

from pathlib import Path

from vat.utils import detect_source, sanitize_filename


def test_detect_source_youtube():
    assert detect_source("https://www.youtube.com/watch?v=abc123") == "youtube"
    assert detect_source("https://youtu.be/abc123") == "youtube"


def test_detect_source_bilibili():
    assert detect_source("https://www.bilibili.com/video/BV1xxx") == "bilibili"


def test_detect_source_local(tmp_path):
    f = tmp_path / "video.mp4"
    f.write_text("fake")
    assert detect_source(str(f)) == "local"


def test_sanitize_filename():
    assert sanitize_filename("hello/world") == "hello_world"
    assert sanitize_filename("a" * 200) == "a" * 120
