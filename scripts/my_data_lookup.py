# keywords: my data lookup, look in my data, dig through my notes, where did i write, dig my records
# desc: Search your notes, journal, to-dos, expenses and other saved records (search my data milk)
# category: productivity
# usage: search my data <words>
# rawargs: yes
# patterns: \bsearch\s+(my\s+)?(data|notes|records|journal|everything)\b ;; \bwhere did i (write|note|save)\b
# priority: 1
import re
from _lib import args_text, fail
from _backup import data_files
from _files import drop_tokens
q = drop_tokens(args_text().lower(), {"search", "find", "look", "for", "in", "my", "data", "notes", "records", "everything", "journal", "saved", "where", "did", "i", "write", "the"}).split()
if not q: fail("Usage: search my data <words>   e.g. search my data dentist")
SKIP = {"log.jsonl", "history.jsonl", "misses.log", "disabled.json", "undo.json", "routines.json"}
hits = 0
for p in data_files():
    if p.name in SKIP or p.suffix not in {".txt", ".csv", ".json", ".md", ".log"}: continue
    try: lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError: continue
    for i, ln in enumerate(lines, 1):
        low = ln.lower()
        if all(w in low for w in q):
            hits += 1
            if hits <= 40: print(f"  {p.name}:{i}  {ln.strip()[:110]}")
print(f"{hits} match(es)." if hits else f"Nothing found for: {' '.join(q)}")
if hits > 40: print("  (showing the first 40)")
