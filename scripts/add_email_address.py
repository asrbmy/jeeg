# keywords: add email, save email address, email address of, set email, contact email, add email address
# desc: Save an email address for a contact (add email mom mom@example.com)
# category: social
# usage: add email <name> <address>
# rawargs: yes
# patterns: \badd\b.*\bemail\b.*@
# priority: 1
import json, re
from _lib import args_text, data_dir, fail
words = args_text().split()
addr = next((x for x in words if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", x)), None)
rest = [x for x in words if x != addr and x.lower() not in {"add", "save", "set", "email", "address", "for", "of", "contact", "to"}]
name = " ".join(rest).lower().strip()
if not addr or not name: fail("Usage: add email <name> <address>   e.g. add email mom mom@example.com")
f = data_dir() / "emails.json"
c = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
c[name] = addr
f.write_text(json.dumps(c, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Saved {name}: {addr}")
