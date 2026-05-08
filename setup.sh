#!/bin/bash
set -e

echo "=== VAT Setup ==="
echo "Checking dependencies..."

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "ERROR: ffmpeg not found. Install it first:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    exit 1
fi
echo "  ffmpeg: OK"

# Check uv
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv not found. Install it:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "  uv: OK"

# Create venv and install dependencies
echo "Creating virtual environment..."
uv venv

echo "Installing dependencies..."
uv pip install -e .

echo ""
echo "=== Setup complete ==="
echo "Run: uv run python -m vat <url_or_path>"
echo "Or:  uv run vat <url_or_path>"
