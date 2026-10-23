# keywords: old downloads, delete old downloads, clean old downloads, clear downloads older than, remove old downloads, downloads older than
# desc: Move old files from Downloads to a safe holding folder (delete old downloads 90 days)
# category: files
# usage: delete old downloads [days]
# confirm: yes
# rawargs: yes
import re, shutil, time
from _lib import args_text, data_dir, user_dir, human
from _files import unique_path
t = args_text()
preview = bool(re.search(r"\b(preview|dry-run|dry)\b", t, re.I))
m = re.search(r"(\d+)", t)
days = int(m.group(1)) if m else 90
if days < 1: days = 1
if re.search(r"\bmonths?\b", t): days *= 30
if re.search(r"\byears?\b", t): days *= 365
src = user_dir("Downloads")
cut = time.time() - days * 86400
dest = data_dir() / "trash" / time.strftime("downloads-%Y%m%d-%H%M")
n = size = 0
for p in sorted(src.iterdir()):
    try:
        if not p.is_file() or p.is_symlink() or p.name.startswith(".") or p.stat().st_mtime > cut:
            continue
        if p.suffix.lower() in (".crdownload", ".part", ".tmp", ".download"):
            continue
        sz = p.stat().st_size
        if not preview:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(unique_path(dest / p.name)))
        n += 1; size += sz
        if n <= 30: print(("  would move " if preview else "  moved ") + p.name)
    except OSError:
        continue
if not n: print(f"No files older than {days} days in {src}.")
elif preview: print(f"{n} file(s), {human(size)} are older than {days} days. Nothing was moved.")
else: print(f"Moved {n} file(s), {human(size)}, to {dest}\n(Nothing is deleted: delete that folder yourself when you are sure.)")
