# keywords: watch folder, folder watcher, auto move files, auto sort folder, monitor folder, move new files, watch downloads, automatic file mover
# desc: Watch a folder and move new files of a type into another folder (watch folder downloads move pdf to Documents/PDF). Add 'once' to run a single pass.
# category: files
# usage: watch folder <folder> move <types> to <folder>
# confirm: yes
# rawargs: full
# patterns: \bwatch\s+(folder\s+)?\S+\s+move\b ;; \b(folder|downloads)\s+watcher\b
# priority: 1
import re, shutil, time
from pathlib import Path
from _lib import args_text, fail
from _files import resolve_folder, unique_path
t = args_text()
once = bool(re.search(r"\bonce\b", t, re.I))
t = re.sub(r"\bonce\b", " ", t, flags=re.I)
m = re.search(r"watch\s+(?:folder\s+)?(.+?)\s+move\s+(.+?)\s+to\s+(.+)$", t, re.I)
if not m:
    fail("Usage: watch folder downloads move pdf to Documents/PDF   (types: pdf, jpg png, or 'all'; add 'once' for one pass; a relative destination is inside your home folder unless it starts with ./)")
src, kinds, dst = resolve_folder(m.group(1)), m.group(2).lower().replace(",", " ").split(), m.group(3).strip().strip('"\'')
d0 = Path(dst).expanduser()
if not d0.is_absolute():
    d0 = (Path.cwd() / d0) if ((Path.cwd() / d0).exists() or dst.startswith('.') or not (Path.home() / d0).parent.exists()) else (Path.home() / d0)
dst = d0
if not src.is_dir():
    fail("The folder to watch was not found.")
if dst.resolve() == src.resolve():
    fail("The destination must be a different folder.")
exts = None if kinds == ["all"] else {"." + k.lstrip(".") for k in kinds}
PARTIAL = {".crdownload", ".part", ".tmp", ".download", ".partial"}
def sweep():
    n = 0
    for p in src.iterdir():
        if not p.is_file() or p.name.startswith(".") or p.suffix.lower() in PARTIAL:
            continue
        if exts is not None and p.suffix.lower() not in exts:
            continue
        try:
            if time.time() - p.stat().st_mtime < 3:          # still being written
                continue
            dst.mkdir(parents=True, exist_ok=True)
            target = unique_path(dst / p.name)
            shutil.move(str(p), str(target))
            print(f"{time.strftime('%H:%M:%S')}  {p.name} -> {target}", flush=True)
            n += 1
        except OSError as ex:
            print(f"  could not move {p.name}: {ex.strerror or ex}", flush=True)
    return n
if once:
    k = sweep()
    print(f"Moved {k} file(s)." if k else "Nothing to move.")
    raise SystemExit(0)
print(f"Watching {src} for {' '.join(sorted(exts)) if exts else 'all files'} -> {dst}.  Press Ctrl+C to stop.", flush=True)
try:
    while True:
        sweep()
        time.sleep(5)
except KeyboardInterrupt:
    print("\nStopped watching.")
