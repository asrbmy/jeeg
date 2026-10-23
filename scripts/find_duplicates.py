# keywords: duplicates, duplicate files, same files, copies, identical files, repeated files, dedupe
# desc: Find duplicate files in a folder (read-only report)
# category: files
# usage: find duplicates [folder]
import hashlib
from collections import defaultdict
from pathlib import Path
from _lib import args_text, human, user_dir
from _files import resolve_folder, walk_files
p = resolve_folder(args_text(), user_dir("Downloads"))
by_size = defaultdict(list)
for path, st in walk_files(p, seconds=40):
    if 0 < st.st_size <= 500 * 1024 ** 2:
        by_size[st.st_size].append(path)
def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()
groups, wasted = [], 0
for size, paths in by_size.items():
    if len(paths) < 2:
        continue
    by_hash = defaultdict(list)
    for q in paths:
        try:
            by_hash[digest(q)].append(q)
        except OSError:
            pass
    for g in by_hash.values():
        if len(g) > 1:
            groups.append((size, g)); wasted += size * (len(g) - 1)
groups.sort(reverse=True)
for size, g in groups[:20]:
    print(f"\n{human(size)} x {len(g)}")
    for q in g:
        print("   ", q)
print(f"\n{len(groups)} duplicate group(s); about {human(wasted)} could be freed. Nothing was deleted.")
