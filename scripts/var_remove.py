# keywords: unset variable, forget variable, clear variable, delete variable
# desc: Delete a saved variable (remove var rate).
# category: utility
# usage: remove var <name>
# rawargs: full
# patterns: ^\s*(remove|delete|unset|forget|clear)\s+(the\s+)?(var|variable)\b
# priority: 2
import re
from _lib import args_text, fail, var_all, var_save
t = re.sub(r"^\s*(?:remove|delete|unset|forget|clear)\s+(?:the\s+)?(?:var|variable)\s+", "", args_text(), flags=re.I).strip().lstrip("$").lower()
if not re.fullmatch(r"[a-z][a-z0-9_]{0,23}", t):
    fail("Usage: remove var <name>")
vs = var_all()
if t not in vs:
    fail(f"No variable named {t}. See them with: vars")
del vs[t]
var_save(vs)
print(f"Removed ${t}.")
