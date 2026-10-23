# keywords: clipboard history, clip history, saved clipboard, past clipboard, earlier copies, copy history
# desc: List saved clipboard items, or copy one back (clipboard history, clipboard history 2, clear clipboard history)
# category: clipboard
# usage: clipboard history [number | clear]
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
