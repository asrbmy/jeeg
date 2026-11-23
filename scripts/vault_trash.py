# keywords: vault trash, delete note, remove note, remove obsidian note, move note to trash
# desc: Move an Obsidian note to the vault's .trash folder (never deleted for good): vault trash <note>. Can be undone with vault undo. Asks first.
# category: notes
# usage: vault trash <note>
# rawargs: full
# patterns: ^\s*vault\s+(?:trash|delete|remove)\b
# priority: 3
# confirm: yes
import re
from _lib import args_text, fail
from _vault import vault_root, plan_ops, apply
t = re.sub(r"^\s*vault\s+(?:trash|delete|remove)\s*", "", args_text(), flags=re.I).strip()
if not t: fail("Usage: vault trash <note>")
v = vault_root()
desc, changes, originals = plan_ops(v, [{"op": "trash", "note": t}])
apply(v, changes, originals)
print("Done: " + desc[0] + ".  Undo with:  vault undo")
