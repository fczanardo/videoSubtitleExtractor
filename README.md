# UNITY Media Tools

Batch audio extraction from videos and automatic transcription using `ffmpeg` and OpenAI Whisper.

## Project Structure

- `run.bat`: Automated one-click execution pipeline for Windows (activates `.venv`, extracts audio, and transcribes all pending files).
- `config.py`: Centralized configuration module that loads settings from `.env` with fallback defaults.
- `audio_extract.py`: Scans `temp/` for video files and extracts audio into `audio/` as `.mp3`.
- `transcribe.py`: Transcribes audio files from `audio/` into text files using Whisper.
- `.env`: Local configuration file (git-ignored).
- `.envexample`: Template with default configuration values.
- `temp/`: Input directory for video files (created automatically if missing).
- `audio/`: Output directory for generated `.mp3` files and transcripts (created automatically if missing).

---

## Quick Start (Automated Pipeline with `run.bat`)

The easiest way to run the entire pipeline on Windows is using `run.bat`. It automatically detects and activates `.venv`, ensures `ffmpeg` availability, extracts audio from all videos in `temp/`, and transcribes pending audio files.

### Option 1: Double-click (Windows Explorer)
1. Place your video files (`.mp4`, `.mov`, `.mkv`, etc.) inside the `temp/` folder.
2. Double-click `run.bat`.
3. The script will:
   - Activate the virtual environment (`.venv`) if available.
   - Extract the audio of all videos from `temp/` to `audio/` (skips videos already extracted).
   - Transcribe all pending `.mp3` files and save results as `audio/<filename>_TRANSCRICAO.txt` (skips already transcribed files).
   - Keep the console window open at the end so you can inspect the output.

### Option 2: Run via Terminal (Command Prompt / PowerShell)

```bat
:: Run the full automated pipeline (processes all videos and transcribes all pending audios)
run.bat

:: Run the pipeline specifying a specific audio file to transcribe
run.bat meu_video.mp3

:: Force re-transcribing all files
run.bat --force
```

---

## Environment Configuration (`.env` & `.envexample`)

All hardcoded settings are now migrated to environment variables and loaded automatically from a local `.env` file via `config.py`.

A template named [`.envexample`](.envexample) (and `.env.example`) is provided in the repository.

### Initial Configuration

To customize your configuration, copy `.envexample` to `.env`:

```bash
# On Windows Command Prompt:
copy .envexample .env

# On PowerShell:
Copy-Item .envexample .env
```

### Configuration Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `TEMP_DIR` | `temp` | Path to the directory where input video files are located. |
| `AUDIO_DIR` | `audio` | Path to the directory where extracted `.mp3` files and transcripts are saved. |
| `VIDEO_EXTENSIONS` | `.mp4,.mov,.mkv,.avi,.m4v,.webm` | Comma-separated list of video extensions to scan and process. |
| `AUDIO_CODEC` | `libmp3lame` | Audio codec used by `ffmpeg` for extraction. |
| `AUDIO_BITRATE` | `96k` | Audio bitrate for extracted `.mp3` files. |
| `AUDIO_SAMPLE_RATE` | `16000` | Audio sampling frequency (Hz), optimized for Whisper (16 kHz). |
| `AUDIO_CHANNELS` | `1` | Number of audio channels (1 = mono, ideal for speech recognition). |
| `WHISPER_MODEL` | `base` | Whisper model to use (`tiny`, `base`, `small`, `medium`, `large`). |
| `WHISPER_LANGUAGE` | *(empty)* | Audio language code (e.g., `pt`, `en`). Leave empty for automatic detection. |
| `WHISPER_FP16` | `False` | Whether to use FP16 half-precision (`True` for GPU, `False` for CPU). |
| `WHISPER_VERBOSE` | `True` | Display real-time transcription segments in the console (`True`/`False`). |
| `TRANSCRIPT_SUFFIX` | `_TRANSCRICAO.txt` | Suffix for the generated transcript text files. |

> **Note on `temp/` and `audio/` folders:**
> If the `temp/` or `audio/` folders do not exist, they are **automatically created** upon execution. If `temp/` is empty, the scripts notify you and exit cleanly without errors.

---

## Transcription Model & API Keys

### Does it require an API Key?
**No API key is required.** The transcription is **100% free, offline, and runs locally** on your machine.
- It does **not** call cloud APIs (such as OpenAI API, ChatGPT, Claude, or Gemini).
- No account or credit card is needed.
- Your audio files and transcripts never leave your computer.

### How does it work?
- The project uses **OpenAI Whisper** via the open-source library (`openai-whisper`).
- On its first run, Whisper automatically downloads the neural network weights (~145 MB for the default `base` model) directly to your local user cache folder (`~/.cache/whisper`).
- Subsequent runs use the cached weights offline and execute on your local hardware (CPU or GPU).

### Available Whisper Models
By default, the `base` model is used (`WHISPER_MODEL=base` in `.env`). You can change the model directly in `.env` or pass the `--model` argument:

| Model | Weights Size | Speed | Relative Accuracy | Recommended For |
| :--- | :--- | :--- | :--- | :--- |
| `tiny` | ~75 MB | ⚡ Fastest | Basic | Quick tests, fast turnaround |
| **`base`** *(default)* | **~145 MB** | **🚀 Fast** | **Good** | **General purpose, balanced** |
| `small` | ~480 MB | ⏱ Moderate | High | Good precision for Portuguese & multiple languages |
| `medium` | ~1.5 GB | 🐢 Slower | Very High | Complex audio, varied accents, background noise |
| `large` | ~3.0 GB | 🐌 Slowest | Maximum | Highest quality (best when running on NVIDIA GPU) |

---

## Requirements

- Python 3.10+
- `ffmpeg` in PATH (or `imageio-ffmpeg` installed via requirements; automatically detected via fallback `.ffmpeg-bin/`)

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

# 4. Copy environment configuration
copy .envexample .env
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
# Transcribes all pending .mp3 files in audio/
python transcribe.py

# Transcribes a specific audio file inside audio/
python transcribe.py meu_video.mp3

# Use a specific model on the fly
python transcribe.py --model small

# Force re-transcription even if transcript already exists
python transcribe.py --force
```

The resulting transcript will be saved in `audio/<audio_name>_TRANSCRICAO.txt`.
