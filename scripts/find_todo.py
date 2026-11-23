# keywords: find todo, find fixme, todo comments, list todos in code, fixme comments, leftover todo
# desc: List TODO, FIXME and HACK comments in a project folder (find todo myproject)
# category: developer
# usage: find todo [folder]
# rawargs: full
# patterns: ^\s*find\s+(?:todo|todos|fixme)s?\b
# priority: 3
import re
from _lib import args_text
from _devscan import root_from, walk, read_text
t = re.sub(r"^\s*find\s+(?:todo|todos|fixme)s?\s*(?:in|of|for)?\s*", "", args_text(), flags=re.I)
root = root_from(t)
pat = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b[:\s(]*(.*)")
hits = []
for p in walk(root):
    s = read_text(p)
    if s is None:
        continue
    for i, line in enumerate(s.splitlines(), 1):
        m = pat.search(line)
        if m and any(c in line[: m.start()] for c in "#/*;-<") :
            hits.append((p, i, m.group(1), m.group(2).strip()[:100]))
if not hits:
    print(f"No TODO or FIXME comments found in {root}.")
for p, i, k, txt in hits[:200]:
    try: rel = p.relative_to(root)
    except ValueError: rel = p
    print(f"{rel}:{i}  {k}  {txt}")
if hits:
    print(f"\n{len(hits)} found" + (" (showing the first 200)" if len(hits) > 200 else "") + f" in {root}")
