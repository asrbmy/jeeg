# keywords: create folder, new folder, make folder, make directory, mkdir, new directory, add folder
# desc: Create a new folder on your Desktop (create folder projects)
# category: files
# usage: create folder <name>
import re
from pathlib import Path
from _lib import args_text, fail
name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", args_text()).strip(" .")
if not name:
    fail("Usage: create folder <name>")
base = next((Path.home() / n for n in ("Desktop", "OneDrive/Desktop") if (Path.home() / n).is_dir()), Path.home())
p = base / name
if p.exists():
    fail(f"Already exists: {p}")
p.mkdir()
print(f"Created {p}")
