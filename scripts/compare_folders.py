# keywords: compare folders, diff folders, folder difference, compare directories, are folders the same, sync check, folder compare, what is different between folders
# desc: Compare two folders: what is only in one, and what differs (compare folders a b)
# category: files
# usage: compare folders <a> <b>
# rawargs: yes
import hashlib, os
from _lib import args_text, fail
from _files import path_arg, tokens, split_on, walk_files
t = args_text()
a_t, b_t = split_on(t, "with") if " with " in t.lower() else split_on(t, "and") if " and " in t.lower() else split_on(t, "vs")
ps = [a_t, b_t] if b_t else tokens(t)
ps = [x for x in ps if x.lower() not in ("compare", "folders", "folder")]
if len(ps) != 2: fail("Usage: compare folders <folder1> <folder2>")
a, b = path_arg(ps[0]), path_arg(ps[1])
if not (a.is_dir() and b.is_dir()): fail("Give two folders.")
def scan(r):
    d = {}
    for p, st in walk_files(r, seconds=30, hidden=True):
        d[os.path.relpath(p, r)] = (p, st.st_size)
        if len(d) > 50000: fail("Too many files (limit 50,000).")
    return d
A, B = scan(a), scan(b)
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()
only_a, only_b = sorted(set(A) - set(B)), sorted(set(B) - set(A))
diff, same = [], 0
for k in sorted(set(A) & set(B)):
    if A[k][1] != B[k][1] or sha(A[k][0]) != sha(B[k][0]): diff.append(k)
    else: same += 1
for title, rows in (("Only in " + a.name, only_a), ("Only in " + b.name, only_b), ("Different content", diff)):
    if rows:
        print(f"{title} ({len(rows)}):")
        for r in rows[:25]: print("  " + r)
        if len(rows) > 25: print(f"  ... and {len(rows) - 25} more")
print(f"{same} identical file(s). " + ("The folders match exactly." if not (only_a or only_b or diff) else ""))
