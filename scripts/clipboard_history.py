# keywords: clipboard history, search clipboard history, find in clipboard history, clip history, saved clipboard, past clipboard, earlier copies, copy history
# desc: List saved clipboard items, find one by a word, or copy one back (clipboard history, search clipboard history invoice, clipboard history 2, clear clipboard history)
# category: clipboard
# usage: clipboard history [number | clear | search <word>]
# rawargs: full
# private: yes
# patterns: \b(clipboard|clip|copy)\s+history\b ;; \b(saved|past|earlier|previous)\s+(clipboard|copies)\b
# priority: 2
import re, time
from _lib import args_text, fail
from _store import load, save
from _sys import clip_set
t = args_text().lower()
h = load("clipboard_history.json", [])
if re.search(r"\b(clear|delete|wipe|erase|empty)\b", t):
    save("clipboard_history.json", [])
    print("Clipboard history cleared.")
    raise SystemExit(0)
if not h:
    fail("Nothing saved yet. Copy something, then say: save clipboard")
if re.search(r"\b(search|find|look)\b", t):
    words = [w for w in re.sub(r"\b(search|find|look|in|for|my|the|clipboard|clip|history|something|what|i|copied|up)\b", " ", t).split() if w]
    if not words:
        fail("Say what to look for, for example:  search clipboard history invoice")
    hits = [(len(h) - i, x) for i, x in enumerate(h) if all(w in x["t"].lower() for w in words)]
    if not hits:
        print(f"No saved clipboard item has: {' '.join(words)}")
        raise SystemExit(0)
    print(f"{len(hits)} saved item(s) with '{' '.join(words)}' (newest first). Copy one back with:  clipboard history <number>")
    for n, x in list(reversed(hits))[:10]:
        one = " ".join(x["t"].split())
        print(f"  {n:>2}. {time.strftime('%d %b %H:%M', time.localtime(x['at']))}  {one[:70]}{'...' if len(one) > 70 else ''}")
    raise SystemExit(0)
m = re.search(r"\b(\d+)\b", t)
if m:
    i = int(m.group(1))
    if not 1 <= i <= len(h):
        fail(f"Pick a number from 1 to {len(h)}.")
    item = h[-i]["t"]
    clip_set(item)
    print(f"Copied item {i} back to the clipboard ({len(item)} characters).")
else:
    print("Saved clipboard items (newest first). Say 'clipboard history <number>' to copy one back:")
    for i, x in enumerate(reversed(h[-15:]), 1):
        one = " ".join(x["t"].split())
        print(f"  {i:>2}. {time.strftime('%d %b %H:%M', time.localtime(x['at']))}  {one[:70]}{'...' if len(one) > 70 else ''}")
