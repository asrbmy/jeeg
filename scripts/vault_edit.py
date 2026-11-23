# keywords: vault replace, vault cut, vault prepend, change text in note, edit note, remove text from note, replace text in obsidian note
# desc: Edit one Obsidian note: vault replace <note> | <old text> | <new text>, vault cut <note> | <text to remove>, vault prepend <note> | <text>. Backs up first (vault undo). Asks first.
# category: notes
# usage: vault replace <note> | <old> | <new>   or   vault cut <note> | <text>   or   vault prepend <note> | <text>
# rawargs: full
# patterns: ^\s*vault\s+(?:replace|cut|prepend)\b
# priority: 3
# confirm: yes
import re
from _lib import args_text, fail
from _vault import vault_root, plan_ops, preview, apply
t = re.sub(r"^\s*vault\s*", "", args_text(), flags=re.I).strip()
cmd, _, rest = t.partition(" ")
cmd = cmd.lower()
parts = [x.strip() for x in rest.split("|")]
if cmd == "replace" and len(parts) == 3 and parts[0] and parts[1]: op = {"op": "replace", "note": parts[0], "find": parts[1], "with": parts[2]}
elif cmd == "cut" and len(parts) == 2 and parts[0] and parts[1]: op = {"op": "remove_text", "note": parts[0], "find": parts[1]}
elif cmd == "prepend" and len(parts) == 2 and parts[0] and parts[1]: op = {"op": "prepend", "note": parts[0], "text": parts[1]}
else: fail("Usage: vault replace <note> | <old text> | <new text>    vault cut <note> | <text>    vault prepend <note> | <text>")
v = vault_root()
desc, changes, originals = plan_ops(v, [op])
if not changes: fail("That would not change anything.")
apply(v, changes, originals)
print("Done: " + desc[0] + ".  Undo with:  vault undo")
