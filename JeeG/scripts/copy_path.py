# keywords: copy path, copy file path, full path, path of file, copy folder path, get path, copy location
# desc: Copy a file or folder's full path to the clipboard (copy path of report.pdf)
# category: files
# usage: copy path of <file>
# rawargs: full
from _lib import args_text
from _files import path_arg
from _sys import clip_set
import re
t = re.sub(r"^\s*(?:copy\s+)?(?:the\s+)?(?:full\s+)?(?:file\s+|folder\s+)?(?:path|location)\s*(?:of|to|for)?\s*", "", args_text(), flags=re.I)
p = path_arg(t) if t else __import__("pathlib").Path.cwd()
clip_set(str(p))
print(f"Copied: {p}")
