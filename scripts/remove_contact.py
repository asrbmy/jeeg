# keywords: remove contact, delete contact, forget contact, erase contact, remove number
# desc: Delete a saved contact (remove contact mom)
# category: social
# usage: remove contact <name>
# confirm: yes
# rawargs: yes
# patterns: \b(remove|delete|forget)\s+(the\s+)?contact\b
# priority: 1
import json
from _lib import args_text, data_dir, fail
from _files import drop_tokens
q = drop_tokens(args_text().lower(), {"remove", "delete", "forget", "erase", "contact", "number", "the"}).strip()
if not q: fail("Usage: remove contact <name>")
gone = False
for fn in ("contacts.json", "emails.json"):
    f = data_dir() / fn
    if not f.exists(): continue
    c = json.loads(f.read_text(encoding="utf-8"))
    if q in c:
        del c[q]; gone = True
        f.write_text(json.dumps(c, indent=1, ensure_ascii=False), encoding="utf-8")
if not gone: fail(f"No contact named '{q}'. See: show contacts")
print(f"Removed {q}.")
