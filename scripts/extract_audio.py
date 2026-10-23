# keywords: extract audio, video to mp3, mp4 to mp3, get audio from video, rip audio, convert video to audio, save audio
# desc: Save the sound of a video as MP3 (extract audio movie.mp4)
# category: media
# usage: extract audio <video file>
# rawargs: yes
import shutil, subprocess
from _lib import args_text, fail
from _files import path_arg, unique_path
if not shutil.which("ffmpeg"): fail("ffmpeg is not installed. Windows: winget install ffmpeg | Mac: brew install ffmpeg | Linux: sudo apt install ffmpeg")
p = path_arg(args_text())
if p.is_dir(): fail("Give a video file, not a folder.")
out = unique_path(p.with_suffix(".mp3"))
rc = subprocess.call(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(p), "-vn", "-acodec", "libmp3lame", "-q:a", "2", str(out)])
if rc: fail("ffmpeg could not read audio from that file.")
print(f"Saved {out}")
