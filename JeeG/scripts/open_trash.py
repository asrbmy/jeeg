# keywords: recycle bin, trash, deleted files, bin, recycle
# desc: Open the Recycle Bin / Trash
# category: folders
import subprocess
from pathlib import Path
from _lib import LINUX, MAC, WIN, open_path
if WIN:
    subprocess.Popen(["explorer", "shell:RecycleBinFolder"])
elif MAC:
    open_path(Path.home() / ".Trash")
else:
    subprocess.Popen(["xdg-open", "trash:///"])
