# keywords: find file, search file, locate, where is, find document, find my, look for file, file search
# desc: Find files by name under your home folder (find file invoice pdf)
# category: files
# usage: find file <name words>
import fnmatch
from pathlib import Path
from _lib import args_text, fail, human
from _files import walk_files
q = [x.lower() for x in args_text().split() if x.lower() not in ("file", "files", "named", "called")]
if not q:
    fail("Usage: find file <part of the name>   e.g. find file invoice pdf")
hits = []
for path, st in walk_files(Path.home(), seconds=20):
    name = Path(path).name.lower()
    if all(w in name for w in q) or (any(c in q[0] for c in "*?") and fnmatch.fnmatch(name, q[0])):
        hits.append((st.st_mtime, path, st.st_size))
        if len(hits) >= 500:
            break
hits.sort(reverse=True)
import time
for mt, path, size in hits[:25]:
    print(f"{time.strftime('%Y-%m-%d', time.localtime(mt))}  {human(size):>9}  {path}")
print(f"{len(hits)} match(es)" + (", showing the 25 newest" if len(hits) > 25 else "") if hits else "No files found.")
