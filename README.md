# UNITY Media Tools

Batch audio extraction from videos and automatic transcription using `ffmpeg` and OpenAI Whisper.

## Project Structure

- `run.bat`: Automated one-click execution pipeline for Windows (activates `.venv`, extracts audio, and transcribes).
- `audio_extract.py`: Scans `temp/` for video files and extracts audio into `audio/` as `.mp3`.
- `transcribe.py`: Transcribes audio files from `audio/` into text files using Whisper (`base` model).
- `temp/`: Input directory for video files.
- `audio/`: Output directory for generated `.mp3` files and `*_TRANSCRICAO.txt` transcripts.

---

## Quick Start (Automated Pipeline with `run.bat`)

The easiest way to run the entire pipeline on Windows is using `run.bat`. It automatically detects and activates `.venv`, extracts audio from videos in `temp/`, and transcribes them.

### Option 1: Double-click (Windows Explorer)
1. Place your video files (`.mp4`, `.mov`, `.mkv`, etc.) inside the `temp/` folder.
2. Double-click `run.bat`.
3. The script will:
   - Activate the virtual environment (`.venv`) if available.
   - Extract the audio of all videos from `temp/` to `audio/`.
   - Transcribe the audio and save the output as `audio/<filename>_TRANSCRICAO.txt`.
   - Keep the console window open at the end so you can inspect the output.

### Option 2: Run via Terminal (Command Prompt / PowerShell)

```bat
:: Run the full automated pipeline (processes all videos in temp/ and transcribes the first available audio)
run.bat

:: Run the pipeline specifying a specific audio file to transcribe
run.bat meu_video.mp3
```

---

## Requirements

- Python 3.10+
- `ffmpeg` available in PATH (or `imageio-ffmpeg` installed via requirements)

---

## Setup & Installation

If configuring manually or setting up for the first time:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Manual Execution (Step-by-step)

If you prefer to run the scripts individually instead of using `run.bat`:

### 1. Extract Audio from Videos
Place your video files in `temp/` and run:

```bash
python audio_extract.py
```

Generated `.mp3` files will be saved in `audio/`. Existing audio files are skipped.

### 2. Transcribe Audio
Transcribe audio files using OpenAI Whisper:

```bash
# Transcribes the first .mp3 found in audio/
python transcribe.py

# Transcribes a specific audio file inside audio/
python transcribe.py meu_video.mp3
```

The resulting transcript will be saved in `audio/<audio_name>_TRANSCRICAO.txt`.

---

## Supported Video Extensions

- `.mp4`
- `.mov`
- `.mkv`
- `.avi`
- `.m4v`
- `.webm`
