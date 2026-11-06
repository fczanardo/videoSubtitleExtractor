from pathlib import Path
import os
import shutil
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "audio"
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm"}

def ensure_ffmpeg_available() -> str:
	if shutil.which("ffmpeg") is not None:
		return "ffmpeg"

	fallback_dir = BASE_DIR / ".ffmpeg-bin"
	fallback_exe = fallback_dir / "ffmpeg.exe"
	if fallback_exe.exists():
		os.environ["PATH"] = f"{fallback_dir.resolve()}{os.pathsep}{os.environ.get('PATH', '')}"
		return str(fallback_exe)

	try:
		import imageio_ffmpeg
		bundled_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
		fallback_dir.mkdir(exist_ok=True)
		if not fallback_exe.exists():
			shutil.copy2(bundled_exe, fallback_exe)
		os.environ["PATH"] = f"{fallback_dir.resolve()}{os.pathsep}{os.environ.get('PATH', '')}"
		return str(fallback_exe)
	except Exception:
		return "ffmpeg"

videos = sorted(
	video_path
	for video_path in TEMP_DIR.iterdir()
	if video_path.is_file() and video_path.suffix.lower() in VIDEO_EXTENSIONS
)

if not videos:
	print(f"No videos found in: {TEMP_DIR}")
	sys.exit(0)

ffmpeg_bin = ensure_ffmpeg_available()

for video_path in videos:
	audio_path = OUTPUT_DIR / f"{video_path.stem}.mp3"

	if audio_path.exists():
		print(f"Already exists, skipping: {audio_path.name}")
		continue

	print(f"Extracting audio: {video_path.name} -> {audio_path.name}")

	# Use ffmpeg directly to improve speed and avoid MoviePy overhead.
	cmd = [
		ffmpeg_bin,
		"-y",
		"-i",
		str(video_path),
		"-vn",
		"-ac",
		"1",
		"-ar",
		"16000",
		"-c:a",
		"libmp3lame",
		"-b:a",
		"96k",
		str(audio_path),
	]

	try:
		result = subprocess.run(cmd, check=False, capture_output=True, text=True)
	except KeyboardInterrupt:
		print("Process interrupted by user.")
		sys.exit(1)

	if result.returncode != 0:
		print(f"Failed to process: {video_path.name}")
		print(result.stderr.strip())
		continue

	print(f"Done: {audio_path.name}")
