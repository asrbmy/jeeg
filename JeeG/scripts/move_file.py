# keywords: move file, move folder, move to, relocate file, move this file, move document, cut and paste file
# desc: Move a file or folder (move file report.pdf to documents)
# category: files
# usage: move file <file> to <folder>
# rawargs: yes
import shutil
from _lib import args_text, fail
from _files import path_arg, split_on, unique_path
src_t, dst_t = split_on(args_text(), "to")
if not dst_t: fail("Usage: move file <file> to <folder>   e.g. move file report.pdf to documents")
src = path_arg(src_t); dst = path_arg(dst_t)
if not dst.is_dir(): fail(f"The destination must be an existing folder: {dst}")
if src == dst or dst.is_relative_to(src): fail("Cannot move a folder into itself.")
if src.parent == dst: fail("It is already there.")
home = __import__("pathlib").Path.home().resolve()
if src in (home, __import__("pathlib").Path(src.anchor)): fail("Refusing to move your home folder or drive.")
out = unique_path(dst / src.name)
shutil.move(str(src), str(out))
print(f"Moved to {out}")
