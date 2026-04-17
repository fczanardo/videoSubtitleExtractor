# UNITY Media Tools

Simple batch audio extraction from videos using `ffmpeg`.

## Current Project Structure

- `audio_extract.py`: Scans `temp/` for video files and extracts audio to `audio/`.
- `temp/`: Input folder for videos.
- `audio/`: Output folder for generated `.mp3` files.

## Requirements

- Python 3.10+
- `ffmpeg` available in PATH

You can verify `ffmpeg` with:

```bash
ffmpeg -version
```

## Setup

If you use a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## How To Use

1. Put your video files into `temp/`.
2. Run:

```bash
python audio_extract.py
```

3. Find generated `.mp3` files in `audio/`.

## Supported Video Extensions

- `.mp4`
- `.mov`
- `.mkv`
- `.avi`
- `.m4v`
- `.webm`

## Behavior Notes

- Output files are named using the video filename stem (example: `clip.mp4` -> `clip.mp3`).
- If an output file already exists, it is skipped.
- If no videos are found in `temp/`, the script exits cleanly.
- Pressing `Ctrl+C` interrupts processing safely.
