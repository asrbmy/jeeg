# keywords: text diff, diff files, difference between files, what changed between files, compare text files, file diff
# desc: Show the differences between two text files (text diff a.txt b.txt)
# category: developer
# usage: text diff <file1> <file2>
# rawargs: full
# priority: 1
import difflib, re
from _lib import args_text, fail
from _files import path_arg, tokens, is_text_file
t = re.sub(r"^\s*(?:please\s+)?(?:text\s+)?(?:diff|difference)\s*(?:between|of)?\s*", "", args_text(), flags=re.I)
parts = tokens(t)
parts = [x for x in parts if x.lower() not in {"and", "with", "vs", "to"}]
if len(parts) != 2: fail("Usage: text diff <file1> <file2>")
a, b = path_arg(parts[0]), path_arg(parts[1])
for f in (a, b):
    if not is_text_file(f): fail(f"{f.name} does not look like a text file.")
la, lb = a.read_text(encoding="utf-8", errors="replace").splitlines(), b.read_text(encoding="utf-8", errors="replace").splitlines()
d = list(difflib.unified_diff(la, lb, a.name, b.name, lineterm="", n=2))
if not d: print("The files are identical.")
else:
    for ln in d[:200]: print(ln)
    if len(d) > 200: print(f"... {len(d) - 200} more line(s)")
