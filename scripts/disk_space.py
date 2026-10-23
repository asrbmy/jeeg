# keywords: disk, storage, drive, drives, space, free space, hard disk, ssd, capacity
# desc: Show free space on your drives
# category: system
import os, shutil, string
from _lib import WIN, human
roots = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")] if WIN else ["/"]
if not WIN:
    for extra in ("/home", "/Volumes", "/mnt", "/media"):
        if os.path.isdir(extra):
            roots += [os.path.join(extra, n) for n in sorted(os.listdir(extra)) if os.path.ismount(os.path.join(extra, n))] if extra != "/home" else ([extra] if os.path.ismount(extra) else [])
for r in roots:
    try:
        t, u, f = shutil.disk_usage(r)
    except OSError:
        continue
    if t:
        print(f"{r:<18} {human(u):>9} used / {human(t):>9}  ({100 * u / t:.0f}%)  free {human(f)}")
