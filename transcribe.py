import argparse
import os
import shutil
import sys
from pathlib import Path
import whisper

from config import (
    BASE_DIR,
    TEMP_DIR,
    AUDIO_DIR,
    WHISPER_MODEL,
    WHISPER_LANGUAGE,
    WHISPER_FP16,
    WHISPER_VERBOSE,
    TRANSCRIPT_SUFFIX,
)

def ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is not None:
        return

    fallback_dir = BASE_DIR / ".ffmpeg-bin"
    fallback_exe = fallback_dir / "ffmpeg.exe"
    if fallback_exe.exists():
        os.environ["PATH"] = f"{fallback_dir.resolve()}{os.pathsep}{os.environ.get('PATH', '')}"
        return

    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise RuntimeError(
            "ffmpeg not found in PATH. Install ffmpeg or run: pip install imageio-ffmpeg"
        ) from exc

    bundled_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
    fallback_dir.mkdir(exist_ok=True)

    if not fallback_exe.exists():
        shutil.copy2(bundled_exe, fallback_exe)

    os.environ["PATH"] = f"{fallback_dir.resolve()}{os.pathsep}{os.environ.get('PATH', '')}"

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is still unavailable in this terminal session.")

parser = argparse.ArgumentParser(description="Transcribe audio file(s) with Whisper.")
parser.add_argument(
    "audio",
    nargs="?",
    help="Optional input audio filename (inside the audio directory). If not provided, transcribes all pending .mp3 files.",
)
parser.add_argument(
    "--model",
    default=WHISPER_MODEL,
    help=f"Whisper model to use (default: {WHISPER_MODEL}). Options: tiny, base, small, medium, large.",
)
parser.add_argument(
    "--lang",
    default=WHISPER_LANGUAGE,
    help=f"Language code (e.g., pt, en). Default from .env: '{WHISPER_LANGUAGE or 'auto'}'.",
)
parser.add_argument(
    "--force",
    action="store_true",
    help="Force re-transcription even if the transcript file already exists.",
)
args = parser.parse_args()

selected_model = args.model or WHISPER_MODEL
selected_lang = args.lang or WHISPER_LANGUAGE

if args.audio:
    target_path = AUDIO_DIR / Path(args.audio).name
    if not target_path.exists():
        print(f"Audio file not found: {target_path.resolve()}")
        sys.exit(1)
    target_files = [target_path]
else:
    target_files = sorted(AUDIO_DIR.glob("*.mp3"))
    if not target_files:
        print(f"No audio files (.mp3) found in '{AUDIO_DIR}'.")
        print(f"If you have videos in '{TEMP_DIR}', extract audio first by running 'audio_extract.py' or 'run.bat'.")
        sys.exit(0)

# Identify pending files
pending_files = []
for file in target_files:
    output_path = AUDIO_DIR / f"{file.stem}{TRANSCRIPT_SUFFIX}"
    if output_path.exists() and not args.force and not args.audio:
        print(f"Already transcribed, skipping: {file.name}")
        continue
    pending_files.append((file, output_path))

if not pending_files:
    print("All audio files are already transcribed.")
    sys.exit(0)

ensure_ffmpeg_available()

print(f"Loading Whisper model ({selected_model})...")
model = whisper.load_model(selected_model)

for audio_path, output_path in pending_files:
    print(f"\n--- Transcribing: {audio_path.name} ---")
    try:
        transcribe_kwargs = {
            "fp16": WHISPER_FP16,
            "verbose": WHISPER_VERBOSE,
        }
        if selected_lang:
            transcribe_kwargs["language"] = selected_lang

        result = model.transcribe(str(audio_path), **transcribe_kwargs)
    except KeyboardInterrupt:
        print("\nTranscription interrupted by user (Ctrl+C).")
        raise SystemExit(130)

    for segment in result.get("segments", []):
        print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] {segment['text']}")

    output_path.write_text(result.get("text", "").strip() + "\n", encoding="utf-8")
    print(f"Saved transcript to: {output_path.resolve()}")
