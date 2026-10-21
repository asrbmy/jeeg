# keywords: zip, compress, zip folder, compress folder, make zip, archive, pack
# desc: Zip a folder next to itself (zip folder projects)
# category: files
# usage: zip folder <folder>
from _lib import args_text, fail, human
from _files import make_zip, resolve_folder, unique_path
src = resolve_folder(args_text())
if not src.is_dir():
    fail("Give a folder to zip, e.g. zip folder projects")
dest = unique_path(src.parent / (src.name + ".zip"))
n, total = make_zip(src, dest)
print(f"Zipped {n:,} files ({human(total)}) -> {dest}  [{human(dest.stat().st_size)}]")
