# keywords: backup, back up, backup folder, backup files, save copy, make backup, archive folder
# desc: Zip a folder into ~/Backups with a timestamp (backup folder documents)
# category: files
# usage: backup folder <folder>
import time
from _lib import args_text, fail, human
from _files import make_zip, resolve_folder
from pathlib import Path
src = resolve_folder(args_text())
if not src.is_dir():
    fail("Give a folder to back up, e.g. backup folder documents")
dest_dir = Path.home() / "Backups"
dest_dir.mkdir(exist_ok=True)
dest = dest_dir / f"{src.name or 'backup'}_{time.strftime('%Y%m%d_%H%M%S')}.zip"
n, total = make_zip(src, dest)
print(f"Backed up {n:,} files ({human(total)}) -> {dest}  [{human(dest.stat().st_size)}]")
