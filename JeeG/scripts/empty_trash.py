# keywords: empty trash, empty recycle bin, clear trash, clear recycle bin, delete trash, empty bin, purge trash
# desc: Empty the Recycle Bin / Trash permanently
# category: files
# confirm: yes
import shutil, subprocess
from pathlib import Path
from _lib import WIN, MAC, fail
if WIN:
    import ctypes
    rc = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x7)      # no confirmation, no sound, no progress
    if rc not in (0, -2147418113):                                       # S_OK / already empty
        fail("Could not empty the Recycle Bin.")
elif MAC:
    subprocess.run(["osascript", "-e", 'tell application "Finder" to empty the trash'])
elif shutil.which("gio"):
    subprocess.run(["gio", "trash", "--empty"])
else:
    t = Path.home() / ".local/share/Trash"
    for sub in ("files", "info"):
        d = t / sub
        if d.is_dir():
            for e in d.iterdir():
                shutil.rmtree(e, ignore_errors=True) if e.is_dir() and not e.is_symlink() else e.unlink(missing_ok=True)
print("Trash emptied.")
