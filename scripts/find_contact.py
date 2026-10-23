# keywords: find contact, look up contact, whose number, number of, phone number of, contact number
# desc: Look up a saved contact by name (find contact mom)
# category: social
# usage: find contact <name>
# rawargs: yes
# patterns: \bwhose\s+number\b ;; \bfind\s+contact\b
# priority: 1
import json
from _lib import args_text, data_dir, fail
from _files import drop_tokens
q = drop_tokens(args_text().lower(), {"find", "search", "look", "up", "whose", "has", "contact", "contacts", "number", "phone", "of", "for", "who", "is", "whats", "what", "s", "the"}).strip()
if not q: fail("Usage: find contact <name>")
f = data_dir() / "contacts.json"; e = data_dir() / "emails.json"
c = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
em = json.loads(e.read_text(encoding="utf-8")) if e.exists() else {}
hits = sorted(n for n in set(c) | set(em) if q in n)
if not hits: fail(f"No contact matches '{q}'. See all: show contacts")
for n in hits:
    print(f"  {n:<20} " + (f"+{c[n]}" if n in c else "(no number)") + (f"   {em[n]}" if n in em else ""))
