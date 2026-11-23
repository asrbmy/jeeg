# keywords: vault listen, watch clipboard for edits, auto apply ai edits, vault watch, vault session, listen for ai edits
# desc: Leave this running while you chat with claude.ai, DeepSeek or ChatGPT: when you copy an AI's edit block, JeeG shows what it would change and asks y/n to apply it. Ctrl+C to stop. Terminal only.
# category: notes
# usage: vault listen [count]
# rawargs: full
# patterns: ^\s*vault\s+(?:listen|watch|session)\b
# priority: 3
import os, re, sys, time
from _lib import args_text, fail
from _sys import clip_get
from _vault import vault_root, parse_ops, plan_ops, preview, apply, undo
if os.environ.get("JEEG_VIA_AI"): fail("This is only for you at the keyboard, not for an AI connection.")
if not sys.stdin.isatty(): fail("Run this in a terminal window, because it asks you questions.")
t = re.sub(r"^\s*vault\s+(?:listen|watch|session)\s*", "", args_text(), flags=re.I).strip()
limit = int(t) if t.isdigit() else 0
v = vault_root()
seen, done = clip_get() or "", 0          # what is already on the clipboard is ignored; only new copies count
print(f"Listening on the clipboard for edit blocks for {v.name}.  Copy an AI's ```jeeg block and I will show it.  (u = undo the last change, Ctrl+C = stop)")
try:
    while True:
        time.sleep(0.8)
        try: cur = clip_get() or ""
        except SystemExit: raise
        except Exception: continue
        if cur == seen or "\"op\"" not in cur: seen = cur; continue
        seen = cur
        try: desc, changes, originals = plan_ops(v, parse_ops(cur))
        except SystemExit as e:
            print("That block cannot be applied. See above; fix it or ask the AI again."); continue
        if not changes: print("That block would not change anything."); continue
        print("\n" + "\n".join("  " + d for d in desc) + "\n\n" + preview(v, changes, originals))
        a = input("Apply? [y/N/u] ").strip().lower()
        if a == "y":
            apply(v, changes, originals); print("Done. (u undoes it)"); done += 1
        elif a == "u": print(f"Put back {undo(v)} note(s).")
        else: print("Not applied.")
        if limit and done >= limit: break
except KeyboardInterrupt:
    print("\nStopped.")
