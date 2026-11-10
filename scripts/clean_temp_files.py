# keywords: clean, cleanup, temp, temporary, junk, temp files, free space, clear cache, delete temp, clean up pc, speed up
# desc: Delete temporary files older than 24 hours (clean temp files preview shows what would go)
# usage: clean temp files [preview]
# category: files
# confirm: yes
import os, shutil, tempfile, time
from pathlib import Path
from _lib import human, args_text
preview = any(w in {"preview", "dry-run", "dryrun"} for w in args_text().lower().split())
root = Path(tempfile.gettempdir())
cutoff = time.time() - 86400
freed = removed = 0
for entry in list(os.scandir(root)):
    try:
        st = entry.stat(follow_symlinks=False)
        if st.st_mtime > cutoff:
            continue
        if hasattr(os, "getuid") and st.st_uid != os.getuid():
            continue                      # never touch other users' or the system's files
        if entry.is_symlink() or entry.is_file(follow_symlinks=False):
            if not preview:
                os.remove(entry.path)
            freed += st.st_size; removed += 1
        elif entry.is_dir(follow_symlinks=False):
            size = sum(f.stat().st_size for f in Path(entry.path).rglob("*") if f.is_file() and not f.is_symlink())
            if not preview:
                shutil.rmtree(entry.path)
            freed += size; removed += 1
    except OSError:
        pass            # in use or protected: leave it alone
print(f"Preview of {root}: {removed} item(s) would be removed, freeing {human(freed)}. Nothing was changed." if preview else f"Cleaned {root}: removed {removed} item(s), freed {human(freed)}.")
