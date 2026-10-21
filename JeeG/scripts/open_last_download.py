# keywords: last download, latest download, newest download, most recent download, open latest file, recent download, just downloaded
# desc: Open the newest file in Downloads
# category: files
from _lib import user_dir, open_path, fail
d = user_dir("Downloads")
c = [p for p in d.iterdir() if p.is_file() and not p.name.startswith(".") and p.suffix.lower() not in (".crdownload", ".part", ".tmp", ".download")]
if not c: fail("Your Downloads folder has no finished files.")
p = max(c, key=lambda x: x.stat().st_mtime)
print(f"Opening {p.name}")
open_path(p)
