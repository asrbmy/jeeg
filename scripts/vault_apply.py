# keywords: vault apply, apply edits to notes, apply ai edits, vault undo, undo vault change, apply changes from clipboard
# desc: Apply the edit block an AI gave you (copied from claude.ai, DeepSeek, ChatGPT...) to your Obsidian notes, with a backup: vault apply (reads the clipboard) or vault apply <json>. vault undo puts the last change back. Asks first.
# category: notes
# usage: vault apply [edit block] | vault undo
# rawargs: full
# patterns: ^\s*vault\s+(?:apply|undo)\b
# priority: 3
# confirm: yes
import re
from _lib import args_text, fail
from _sys import clip_get
from _vault import vault_root, parse_ops, plan_ops, preview, apply, undo
t = re.sub(r"^\s*vault\s*", "", args_text(), flags=re.I).strip()
cmd, _, rest = t.partition(" ")
v = vault_root()
if cmd.lower() == "undo":
    print(f"Put back the notes from the last change ({undo(v)} note(s)).")
else:
    import os
    if not rest.strip() and os.environ.get("JEEG_VIA_AI"): fail("An AI connection must include the edit block in the command; it cannot read your clipboard.")
    text = rest.strip() or clip_get() or ""
    if not text.strip(): fail("Nothing to apply. Copy the AI's edit block first (or paste it after the command).")
    desc, changes, originals = plan_ops(v, parse_ops(text))
    if not changes: fail("Those edits would not change anything.")
    apply(v, changes, originals)
    print("Done:\n  " + "\n  ".join(desc) + "\nUndo with:  vault undo")
