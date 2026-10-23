# keywords: file types, file extensions, what kinds of files, extensions in folder, types of files, count files by type, breakdown of files
# desc: Count files by type in a folder (file types in downloads)
# category: files
# usage: file types in <folder>
import os
from collections import Counter
from _lib import args_text, human
from _files import resolve_folder, walk_files
folder = resolve_folder(args_text().replace("in ", "", 1) if args_text().startswith("in ") else args_text())
cnt, size = Counter(), Counter()
for p, st in walk_files(folder, seconds=20):
    e = os.path.splitext(p)[1].lower() or "(none)"
    cnt[e] += 1; size[e] += st.st_size
if not cnt: print("No files found."); raise SystemExit(0)
print(f"{sum(cnt.values()):,} files, {human(sum(size.values()))} in {folder}")
for e, n in cnt.most_common(15): print(f"  {e:<10}{n:>7,}   {human(size[e])}")
