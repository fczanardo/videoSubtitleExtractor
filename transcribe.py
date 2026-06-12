import argparse
import os
import shutil
from pathlib import Path
import whisper

def ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is not None:
        return

    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise RuntimeError(
            "ffmpeg not found in PATH. Install ffmpeg or run: pip install imageio-ffmpeg"
        ) from exc

    bundled_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
    fallback_dir = Path(".ffmpeg-bin")
    fallback_dir.mkdir(exist_ok=True)
    fallback_exe = fallback_dir / "ffmpeg.exe"

    if not fallback_exe.exists():
        shutil.copy2(bundled_exe, fallback_exe)

    os.environ["PATH"] = f"{fallback_dir.resolve()}{os.pathsep}{os.environ.get('PATH', '')}"

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is still unavailable in this terminal session.")

parser = argparse.ArgumentParser(description="Transcribe an audio file with Whisper.")
parser.add_argument(
    "audio",
    nargs="?",
    help="Input audio filename (inside the 'audio' directory). If not provided, uses the first .mp3 found.",
)
args = parser.parse_args()

audio_dir = Path("audio")
audio_dir.mkdir(exist_ok=True)

if args.audio:
    audio_path = audio_dir / Path(args.audio).name
else:
    mp3_files = list(audio_dir.glob("*.mp3"))
    if not mp3_files:
        raise FileNotFoundError(f"No audio files found in '{audio_dir}'. Please add one or specify its name.")
    audio_path = mp3_files[0]
    print(f"No audio file specified. Using: {audio_path.name}")

if not audio_path.exists():
    raise FileNotFoundError(f"Audio file not found: {audio_path.resolve()}")

output_path = audio_dir / f"{audio_path.stem}_TRANSCRICAO.txt"

ensure_ffmpeg_available()

print("Loading Whisper model (base)...")
model = whisper.load_model("base")

try:
    print("Transcribing audio. This can take a while on CPU; avoid pressing Ctrl+C.")
    result = model.transcribe(str(audio_path), fp16=False, verbose=True)
except KeyboardInterrupt:
    print("Transcription interrupted by user (Ctrl+C).")
    raise SystemExit(130)

for segment in result["segments"]:
    print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] {segment['text']}")

output_path.write_text(result.get("text", "").strip() + "\n", encoding="utf-8")
print(f"Saved transcript to: {output_path.resolve()}")
