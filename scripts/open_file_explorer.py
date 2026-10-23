# keywords: files, explorer, finder, file manager, home folder, my files
# desc: Open the file manager at your home folder
# category: folders
from pathlib import Path
from _lib import open_path
open_path(Path.home())
