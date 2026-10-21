# keywords: clean, cleanup, temp, temporary, junk, temp files, free space, clear cache, delete temp, clean up pc, speed up
# desc: Delete temporary files older than 24 hours
# category: files
# confirm: yes
import os, shutil, tempfile, time
from pathlib import Path
from _lib import human
root = Path(tempfile.gettempdir())
cutoff = time.time() - 86400
freed = removed = 0
for entry in list(os.scandir(root)):
    try:
        st = entry.stat(follow_symlinks=False)
        if st.st_mtime > cutoff:
            continue
        if entry.is_symlink() or entry.is_file(follow_symlinks=False):
            os.remove(entry.path); freed += st.st_size; removed += 1
        elif entry.is_dir(follow_symlinks=False):
            size = sum(f.stat().st_size for f in Path(entry.path).rglob("*") if f.is_file() and not f.is_symlink())
            shutil.rmtree(entry.path); freed += size; removed += 1
    except OSError:
        pass            # in use or protected: leave it alone
print(f"Cleaned {root}: removed {removed} item(s), freed {human(freed)}.")
