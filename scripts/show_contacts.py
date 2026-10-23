# keywords: contacts, show contacts, my contacts, list contacts, phone book, saved numbers
# desc: List your saved contacts
# category: social
import json
from _lib import data_dir
f = data_dir() / "contacts.json"
c = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
if not c:
    print("No contacts yet. Add one: add contact mom 919876543210")
for n, d in sorted(c.items()):
    print(f"  {n:<20} +{d}")
