# keywords: compress video, shrink video, reduce video size, make video smaller, video compress, small video, ffmpeg compress
# desc: Make a video file smaller with ffmpeg (compress video movie.mp4)
# category: media
# usage: compress video <file>
# rawargs: yes
import shutil, subprocess
from _lib import args_text, fail
from _files import path_arg, unique_path
if not shutil.which("ffmpeg"): fail("ffmpeg is not installed. Windows: winget install ffmpeg | Mac: brew install ffmpeg | Linux: sudo apt install ffmpeg")
p = path_arg(args_text())
if p.is_dir(): fail("Give a video file, not a folder.")
out = unique_path(p.with_name(p.stem + "_small.mp4"))
print("Compressing (this can take a while)...")
rc = subprocess.call(["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-i", str(p), "-vcodec", "libx264", "-crf", "28", "-preset", "medium", "-acodec", "aac", "-b:a", "128k", str(out)])
if rc: fail("ffmpeg could not convert that file.")
a, b = p.stat().st_size, out.stat().st_size
print(f"{p.name}: {a / 1048576:.1f} MB -> {out.name}: {b / 1048576:.1f} MB")
