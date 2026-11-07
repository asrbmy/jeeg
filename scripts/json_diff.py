# keywords: json diff, compare json, diff json, json difference, json changes
# desc: Compare two JSON files and list what changed (json diff a.json b.json)
# category: developer
# usage: json diff <old.json> <new.json>
# rawargs: full
# patterns: \bjson\s+diff\b ;; \b(compare|diff)\s+(two\s+)?json\b
# priority: 2
import json, re
from pathlib import Path
from _lib import args_text, fail
SKIP = {"json", "diff", "compare", "difference", "changes", "between", "and", "with", "two"}
paths = [p.strip("\"'") for p in args_text().split() if p.lower() not in SKIP]
if len(paths) != 2:
    fail("Usage: json diff old.json new.json")
def load(p):
    f = Path(p).expanduser()
    if not f.is_file() or f.stat().st_size > 20_000_000:
        fail(f"Cannot read {p} (missing, or over 20 MB).")
    try:
        return json.loads(f.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        fail(f"{p} is not valid JSON: {e}")
a, b = load(paths[0]), load(paths[1])
out = []
def walk(x, y, path):
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y), key=str):
            p = f"{path}.{k}" if path else str(k)
            if k not in y: out.append(f"  - removed  {p}")
            elif k not in x: out.append(f"  + added    {p} = {json.dumps(y[k])[:60]}")
            else: walk(x[k], y[k], p)
    elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        for i, (p, q) in enumerate(zip(x, y)):
            walk(p, q, f"{path}[{i}]")
    elif x != y:
        out.append(f"  ~ changed  {path or '(root)'}: {json.dumps(x)[:40]} -> {json.dumps(y)[:40]}")
walk(a, b, "")
print(f"{len(out)} difference(s):" if out else "The two files hold the same data.")
print("\n".join(out[:200]))
