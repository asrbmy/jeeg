# keywords: compare files, diff files, file difference, are these files the same, compare two files, what changed between files, same file
# desc: Compare two files: same or different, and what changed (compare files a.txt b.txt)
# category: files
# usage: compare files <a> <b>
# rawargs: yes
import difflib, hashlib
from _lib import args_text, fail
from _files import path_arg, tokens, split_on, is_text_file
t = args_text()
a_t, b_t = split_on(t, "with") if " with " in t.lower() else split_on(t, "and") if " and " in t.lower() else split_on(t, "vs")
ps = [a_t, b_t] if b_t else tokens(t)
ps = [x for x in (path_arg(p) for p in (ps if not b_t else [a_t, b_t])) ]
if len(ps) != 2: fail("Usage: compare files <file1> <file2>   (or: compare files a.txt with b.txt)")
a, b = ps
if a.is_dir() or b.is_dir(): fail("Give two files, not folders.")
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()
print(f"{a.name}: {a.stat().st_size:,} bytes\n{b.name}: {b.stat().st_size:,} bytes")
if sha(a) == sha(b): print("IDENTICAL (same content)."); raise SystemExit(0)
print("DIFFERENT.")
if is_text_file(a) and is_text_file(b):
    d = list(difflib.unified_diff(a.read_text(errors="replace").splitlines(), b.read_text(errors="replace").splitlines(), a.name, b.name, lineterm="", n=1))
    print("\n".join(d[:60]) + (f"\n... ({len(d) - 60} more diff lines)" if len(d) > 60 else ""))
