from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

def load_env_file(env_path: Path = BASE_DIR / ".env") -> None:
    """Loads environment variables from .env file with native parsing and python-dotenv fallback."""
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
        return
    except ImportError:
        pass

    if env_path.is_file():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("\"'").strip()
                if key and key not in os.environ:
                    os.environ[key] = val

load_env_file()

def _get_dir(env_var: str, default_name: str) -> Path:
    raw_path = os.getenv(env_var, default_name).strip()
    path = Path(raw_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    path.mkdir(parents=True, exist_ok=True)
    return path

# Directories
TEMP_DIR = _get_dir("TEMP_DIR", "temp")
AUDIO_DIR = _get_dir("AUDIO_DIR", "audio")

# Audio Extraction Settings (ffmpeg)
raw_extensions = os.getenv("VIDEO_EXTENSIONS", ".mp4,.mov,.mkv,.avi,.m4v,.webm")
VIDEO_EXTENSIONS = {
    ext.strip().lower() if ext.strip().startswith(".") else f".{ext.strip().lower()}"
    for ext in raw_extensions.split(",")
    if ext.strip()
}
AUDIO_CODEC = os.getenv("AUDIO_CODEC", "libmp3lame")
AUDIO_BITRATE = os.getenv("AUDIO_BITRATE", "96k")
AUDIO_SAMPLE_RATE = os.getenv("AUDIO_SAMPLE_RATE", "16000")
AUDIO_CHANNELS = os.getenv("AUDIO_CHANNELS", "1")

# Transcription Settings (Whisper)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "").strip() or None
WHISPER_FP16 = os.getenv("WHISPER_FP16", "False").strip().lower() in ("true", "1", "yes")
WHISPER_VERBOSE = os.getenv("WHISPER_VERBOSE", "True").strip().lower() in ("true", "1", "yes")
TRANSCRIPT_SUFFIX = os.getenv("TRANSCRIPT_SUFFIX", "_TRANSCRIPTION.txt")
