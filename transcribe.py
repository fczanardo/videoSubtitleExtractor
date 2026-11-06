import argparse
import os
import shutil
import sys
from pathlib import Path
import whisper

BASE_DIR = Path(__file__).resolve().parent

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
    help="Optional input audio filename (inside the 'audio' directory). If not provided, transcribes all pending .mp3 files.",
)
parser.add_argument(
    "--force",
    action="store_true",
    help="Force re-transcription even if the transcript file already exists.",
)
args = parser.parse_args()

audio_dir = BASE_DIR / "audio"
audio_dir.mkdir(exist_ok=True)

if args.audio:
    target_path = audio_dir / Path(args.audio).name
    if not target_path.exists():
        print(f"Audio file not found: {target_path.resolve()}")
        sys.exit(1)
    target_files = [target_path]
else:
    target_files = sorted(audio_dir.glob("*.mp3"))
    if not target_files:
        print(f"No audio files (.mp3) found in '{audio_dir}'.")
        sys.exit(0)

# Identify pending files
pending_files = []
for file in target_files:
    output_path = audio_dir / f"{file.stem}_TRANSCRICAO.txt"
    if output_path.exists() and not args.force and not args.audio:
        print(f"Already transcribed, skipping: {file.name}")
        continue
    pending_files.append((file, output_path))

if not pending_files:
    print("All audio files are already transcribed.")
    sys.exit(0)

ensure_ffmpeg_available()

print("Loading Whisper model (base)...")
model = whisper.load_model("base")

for audio_path, output_path in pending_files:
    print(f"\n--- Transcribing: {audio_path.name} ---")
    try:
        result = model.transcribe(str(audio_path), fp16=False, verbose=True)
    except KeyboardInterrupt:
        print("\nTranscription interrupted by user (Ctrl+C).")
        raise SystemExit(130)

    for segment in result.get("segments", []):
        print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] {segment['text']}")

    output_path.write_text(result.get("text", "").strip() + "\n", encoding="utf-8")
    print(f"Saved transcript to: {output_path.resolve()}")
