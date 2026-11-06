from pathlib import Path
import os
import shutil
import subprocess
import sys

from config import (
	BASE_DIR,
	TEMP_DIR,
	AUDIO_DIR,
	VIDEO_EXTENSIONS,
	AUDIO_CODEC,
	AUDIO_BITRATE,
	AUDIO_SAMPLE_RATE,
	AUDIO_CHANNELS,
)

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
	print(f"Please place video files ({', '.join(sorted(VIDEO_EXTENSIONS))}) in '{TEMP_DIR}'.")
	sys.exit(0)

ffmpeg_bin = ensure_ffmpeg_available()

for video_path in videos:
	audio_path = AUDIO_DIR / f"{video_path.stem}.mp3"

	if audio_path.exists():
		print(f"Already exists, skipping: {audio_path.name}")
		continue

	print(f"Extracting audio: {video_path.name} -> {audio_path.name}")

	# Use ffmpeg directly with configured parameters
	cmd = [
		ffmpeg_bin,
		"-y",
		"-i",
		str(video_path),
		"-vn",
		"-ac",
		AUDIO_CHANNELS,
		"-ar",
		AUDIO_SAMPLE_RATE,
		"-c:a",
		AUDIO_CODEC,
		"-b:a",
		AUDIO_BITRATE,
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
