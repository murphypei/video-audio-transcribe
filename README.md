# Video Audio Transcribe (VAT)

Download audio from YouTube/Bilibili (or extract from local video files), then transcribe to plain text using local ASR.

## Features

- **Download**: YouTube / Bilibili single videos via `yt-dlp`
- **Extract**: Local video files via `ffmpeg`
- **Transcribe**: Local MLX Whisper (`mlx-community/whisper-large-v3-turbo`) on Apple Silicon
- **Authentication-free**: Uses system Chrome cookies, no account setup needed
- **Batch support**: Process multiple URLs/files in one command
- **Modular**: Each step can run independently

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) (must be in PATH)
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- macOS with Apple Silicon (M1/M2/M3/M4) for MLX Whisper GPU acceleration

## Quick Start

```bash
# 1. Clone and enter repo
git clone <repo-url> && cd video-audio-transcribe

# 2. One-line setup
chmod +x setup.sh && ./setup.sh

# 3. Run
uv run vat "https://www.bilibili.com/video/BV..."
```

## Usage

### Full pipeline (download + transcribe)

```bash
uv run vat "https://www.bilibili.com/video/BV1ACNgzaEW7/"
```

### Batch processing

```bash
uv run vat url1 url2 url3 --output-dir ./downloads
```

### Local video

```bash
uv run vat /path/to/video.mp4 --output-dir ./audio
```

### Step-by-step

```bash
# Only download audio (no transcription)
uv run vat <url> --step download

# Only extract audio from local video
uv run vat video.mp4 --step extract

# Only transcribe existing audio
uv run vat audio.mp3 --step transcribe
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--output-dir` | `./downloads` | Output directory |
| `--format` | `mp3` | Audio format: `mp3` or `wav` |
| `--step` | `all` | Run only one step: `all` / `download` / `extract` / `transcribe` |
| `--json` | | Output results as JSON lines |

## Project Structure

```
video-audio-transcribe/
├── vat/
│   ├── __init__.py
│   ├── utils.py        # Source detection, filename sanitization
│   ├── download.py     # yt-dlp YouTube/Bilibili downloader
│   ├── extract.py      # ffmpeg local video audio extraction
│   ├── transcribe.py   # mlx-whisper local ASR
│   ├── pipeline.py     # End-to-end orchestration
│   └── __main__.py     # CLI entry point
├── tests/
│   └── test_pipeline.py
├── pyproject.toml
├── setup.sh
├── CLAUDE.md
└── README.md
```

## How It Works

### YouTube
- `yt-dlp` with multi `player_client` fallback (`android` → `tv_embedded` → `tv` → `ios`)
- `--cookies-from-browser chrome` for age-restricted or member-only content

### Bilibili
- `yt-dlp` with Chrome cookies for HD and member content
- Automatic best audio stream selection, FFmpeg conversion to mp3/wav

### Local Video
- `ffmpeg` direct audio track extraction
- mp3: 44100Hz stereo 192kbps | wav: 44100Hz stereo 16-bit PCM

### Transcription
- `mlx-whisper` with `whisper-large-v3-turbo` model
- Auto language detection, plain text output (no timestamps)
- Model downloaded once on first use (~1.6GB), then cached locally

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `403 Forbidden` (YouTube) | Check Chrome is logged into YouTube; multi `player_client` fallback is already configured |
| `ffmpeg not found` | `brew install ffmpeg` |
| `yt-dlp is not installed` | Run `./setup.sh` |
| Cookie read fails | Quit Chrome and retry |
| First transcription slow | Model download (~1.6GB); subsequent runs are fast |

## License

MIT
