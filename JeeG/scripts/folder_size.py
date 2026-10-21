# keywords: folder size, size of, how big, directory size, space used by, how much space, du, size of folder
# desc: Show how big a folder is (folder size downloads)
# category: files
# usage: folder size [folder]
from _lib import args_text, human
from _files import resolve_folder, walk_files
p = resolve_folder(args_text())
total = n = 0
for _, st in walk_files(p, seconds=60, skip=set(), hidden=True):
    total += st.st_size; n += 1
print(f"{p}\n  {human(total)} in {n:,} files")
