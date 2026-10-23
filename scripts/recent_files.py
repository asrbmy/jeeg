# keywords: recent, recent files, latest files, recently modified, new files, what did i change, last edited, recently downloaded
# desc: List recently changed files in Documents, Downloads and Desktop
# category: files
import time
from pathlib import Path
from _lib import human
from _files import walk_files
rows = []
for n in ("Documents", "Downloads", "Desktop", "OneDrive/Desktop", "OneDrive/Documents"):
    d = Path.home() / n
    if d.is_dir():
        for path, st in walk_files(d, seconds=8):
            rows.append((st.st_mtime, path, st.st_size))
rows.sort(reverse=True)
for mt, path, size in rows[:20]:
    print(f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(mt))}  {human(size):>9}  {path}")
if not rows:
    print("No files found.")
