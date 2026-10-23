# keywords: tree, folder tree, directory tree, show tree, folder structure, directory structure, list folder contents, show structure
# desc: Show a folder as a tree (folder tree documents, tree depth 3)
# category: files
# usage: folder tree [folder] [depth n]
# rawargs: yes
import os, re
from _lib import args_text
from _files import resolve_folder, SKIP_DIRS
t = args_text()
m = re.search(r"\bdepth\s*(\d+)|\blevels?\s*(\d+)", t, re.I)
depth = int(next(g for g in m.groups() if g)) if m else 2
depth = max(1, min(depth, 6))
root = resolve_folder(re.sub(r"\b(depth|levels?)\s*\d+", " ", t, flags=re.I).strip())
count = [0]
def walk(d, prefix, level):
    try:
        items = sorted(os.scandir(d), key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()))
    except OSError:
        return
    items = [e for e in items if not e.name.startswith(".") and e.name not in SKIP_DIRS]
    for i, e in enumerate(items):
        if count[0] >= 300:
            return
        last = i == len(items) - 1
        isdir = e.is_dir(follow_symlinks=False)
        print(f"{prefix}{'`-- ' if last else '|-- '}{e.name}{'/' if isdir else ''}")
        count[0] += 1
        if isdir and level < depth:
            walk(e.path, prefix + ("    " if last else "|   "), level + 1)
print(root)
walk(root, "", 1)
if count[0] >= 300: print("... (stopped at 300 entries; use a smaller depth or a subfolder)")
