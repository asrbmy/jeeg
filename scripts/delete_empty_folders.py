# keywords: empty folders, remove empty folders, delete empty directories, clean empty folders, empty directories, remove empty dirs
# desc: Remove empty folders inside a folder (add 'preview' to just list them)
# category: files
# usage: delete empty folders <folder>
# confirm: yes
# rawargs: yes
import os, re
from pathlib import Path
from _lib import args_text, fail
from _files import resolve_folder, SKIP_DIRS
t = args_text()
preview = bool(re.search(r"\b(preview|dry-run|dry)\b", t, re.I))
from _files import drop_tokens
t = drop_tokens(t, {"preview", "dry-run", "dry", "in", "inside", "from"})
if not t: fail("Usage: delete empty folders <folder> [preview]   (a folder name is required)")
root = resolve_folder(t)
if root == Path.home().resolve() or root == Path(root.anchor):
    fail("Choose a specific folder, not your whole home folder or drive.")
gone = []
for d, dirs, files in os.walk(root, topdown=False):
    dp = Path(d)
    if dp == root or dp.is_symlink() or any(part in SKIP_DIRS or part.startswith(".") for part in dp.relative_to(root).parts):
        continue
    try:
        empty = not any(os.scandir(dp))
    except OSError:
        continue
    if empty:
        if not preview:
            try: os.rmdir(dp)
            except OSError: continue
        gone.append(dp)
for p in gone[:50]: print(("  would remove " if preview else "  removed ") + str(p))
print(f"{len(gone)} empty folder(s) {'found' if preview else 'removed'} in {root}.")
