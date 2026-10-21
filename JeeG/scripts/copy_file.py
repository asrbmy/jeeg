# keywords: copy file, copy folder, duplicate file, copy to, copy document, make a copy of, clone file
# desc: Copy a file or folder (copy file report.pdf to desktop)
# category: files
# usage: copy file <file> to <folder>
# rawargs: yes
import shutil
from pathlib import Path
from _lib import args_text, fail
from _files import path_arg, split_on, unique_path
src_t, dst_t = split_on(args_text(), "to")
if not dst_t: fail("Usage: copy file <file> to <folder>   e.g. copy file report.pdf to desktop")
src = path_arg(src_t); dst = path_arg(dst_t)
if not dst.is_dir(): fail(f"The destination must be an existing folder: {dst}")
if src.is_dir() and (src == dst or dst.is_relative_to(src)): fail("Cannot copy a folder into itself.")
out = unique_path(dst / src.name)
(shutil.copytree if src.is_dir() else shutil.copy2)(src, out)
print(f"Copied to {out}")
