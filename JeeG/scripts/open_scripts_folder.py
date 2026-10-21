# keywords: scripts folder, task folder, my scripts, tasks folder, add script
# desc: Open the folder holding these task scripts
# category: folders
from pathlib import Path
from _lib import open_path
open_path(Path(__file__).resolve().parent)
