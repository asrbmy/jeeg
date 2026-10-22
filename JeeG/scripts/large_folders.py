# keywords: large folders, biggest folders, what is taking space, disk usage by folder, space hogs, which folder is biggest, folder sizes
# desc: Show which sub-folders take the most space (large folders downloads)
# category: files
# usage: large folders [folder]
# rawargs: full
# priority: 1
import os, time
from _lib import args_text, human
from _files import resolve_folder, drop_tokens
p = resolve_folder(drop_tokens(args_text(), {"large", "largest", "big", "biggest", "folders", "folder", "in", "of", "show", "me", "what", "is", "taking", "space", "disk", "usage", "by", "sizes", "which", "the"}).strip())
end = time.time() + 40
rows, loose, partial = [], 0, False
for e in os.scandir(p):
    if e.is_symlink(): continue
    if e.is_file():
        try: loose += e.stat().st_size
        except OSError: pass
    elif e.is_dir():
        tot = 0
        for r, ds, fs in os.walk(e.path, onerror=lambda x: None):
            for f in fs:
                try:
                    fp = os.path.join(r, f)
                    if not os.path.islink(fp): tot += os.path.getsize(fp)
                except OSError: pass
            if time.time() > end: partial = True; break
        rows.append((tot, e.name))
        if time.time() > end: partial = True
rows.sort(reverse=True)
print(p)
for s, n in rows[:15]: print(f"  {human(s):>10}  {n}")
if loose: print(f"  {human(loose):>10}  (files directly in this folder)")
if not rows and not loose: print("  (empty)")
if partial: print("(stopped after 40 seconds; sizes may be incomplete)")
