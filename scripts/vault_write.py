# keywords: vault add, vault append, add to note, append to note, new note, vault new, write to obsidian, add to my notes
# desc: Add text to the end of an Obsidian note or make a new one: vault append <note> | <text>, vault new <note> | <text>. Never overwrites or deletes; backs up first (vault undo). Asks first.
# category: notes
# usage: vault append <note> | <text>   or   vault new <note> | <text>
# rawargs: full
# patterns: ^\s*vault\s+(?:append|add|new)\b
# priority: 3
# confirm: yes
import re
from _lib import args_text, fail
t = re.sub(r"^\s*vault\s*", "", args_text(), flags=re.I).strip()
cmd, _, rest = t.partition(" ")
cmd = cmd.lower()
name, sep, text = rest.partition("|")
name, text = name.strip().strip("[]"), text.strip()
if cmd not in ("append", "add", "new") or not name or not text:
    fail("Usage: vault append <note> | <text>   or   vault new <note> | <text>")
from _vault import vault_root, plan_ops, apply
v = vault_root()
if len(text) > 20000: fail("That is too much text for one add (20,000 characters).")
op = {"op": "new" if cmd == "new" else "append", "note": name, "text": text}
if cmd == "new":
    from _vault import new_target
    if new_target(v, name).exists(): fail("A note with that name already exists. Use  vault append  to add to it.")
desc, changes, originals = plan_ops(v, [op])
apply(v, changes, originals)
print(("Made " if cmd == "new" else "Added to ") + str(next(iter(changes)).relative_to(v)) + ".  Undo with:  vault undo")
