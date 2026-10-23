# keywords: save clipboard, keep clipboard, remember clipboard, store clipboard, clip save, snapshot clipboard
# desc: Keep what is on the clipboard in your private clipboard history (save clipboard)
# category: clipboard
# usage: save clipboard
# private: yes
# patterns: \b(save|keep|remember|store|snapshot)\s+(the\s+|my\s+)?(current\s+)?clipboard\b ;; \bclip\s+save\b
# priority: 2
import time
from _lib import fail
from _store import load, save
from _sys import clip_get
t = clip_get()
if not t or not t.strip():
    fail("The clipboard is empty or not text.")
t = t[:5000]
h = [x for x in load("clipboard_history.json", []) if x["t"] != t]
h.append({"t": t, "at": int(time.time())})
save("clipboard_history.json", h[-50:])
print(f"Saved ({len(t)} characters). You now have {len(h[-50:])} saved. Say: clipboard history")
