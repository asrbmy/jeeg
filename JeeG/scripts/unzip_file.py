# keywords: unzip, extract, unpack, decompress, extract zip, open zip, un zip, untar
# desc: Extract a .zip / .tar.gz safely (unzip file archive.zip)
# category: files
# usage: unzip file <archive>
import tarfile, zipfile
from pathlib import Path
from _lib import args_text, fail
from _files import unique_path
t = args_text().strip().strip("\"'")
src = Path(t).expanduser()
if not t or not src.is_file():
    fail("Usage: unzip file <path to .zip/.tar.gz>")
base = src.name
for ext in (".tar.gz", ".tar.bz2", ".tar.xz", ".tgz", ".zip", ".tar"):
    if base.lower().endswith(ext):
        base = base[: -len(ext)]; break
dest = unique_path(src.parent / base)
root = dest.resolve()
def safe(name):
    return (root / name).resolve().is_relative_to(root)
if zipfile.is_zipfile(src):
    with zipfile.ZipFile(src) as z:
        bad = [n for n in z.namelist() if not safe(n)]
        if bad: fail("Archive contains unsafe paths; refusing to extract.")
        if sum(i.file_size for i in z.infolist()) > 20 * 1024 ** 3: fail("Archive expands to more than 20 GB; refusing.")
        dest.mkdir(); z.extractall(dest); n = len(z.namelist())
elif tarfile.is_tarfile(src):
    with tarfile.open(src) as tf:
        members = tf.getmembers()
        if any(not safe(m.name) or m.issym() or m.islnk() or m.isdev() for m in members):
            fail("Archive contains unsafe entries; refusing to extract.")
        if sum(m.size for m in members if m.isfile()) > 20 * 1024 ** 3: fail("Archive expands to more than 20 GB; refusing.")
        dest.mkdir()
        try: tf.extractall(dest, filter="data")
        except TypeError: tf.extractall(dest)          # older Python without extraction filters
        n = len(members)
else:
    fail("Not a supported archive (.zip, .tar, .tar.gz, .tgz).")
print(f"Extracted {n} item(s) -> {dest}")
