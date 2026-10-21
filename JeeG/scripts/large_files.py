# keywords: large files, biggest files, big files, space hogs, what is using space, largest, huge files, free up space
# desc: Find the biggest files (large files downloads)
# category: files
# usage: large files [folder]
import heapq
from _lib import args_text, human
from _files import resolve_folder, walk_files
from pathlib import Path
p = resolve_folder(args_text(), Path.home())
top = heapq.nlargest(15, ((st.st_size, path) for path, st in walk_files(p, seconds=40)))
print(f"Largest files under {p}:")
for size, path in top:
    print(f"  {human(size):>9}  {path}")
if not top:
    print("  (none found)")
