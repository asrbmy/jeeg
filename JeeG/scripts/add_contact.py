# keywords: contact, add contact, save contact, new contact, save number, remember number, phone book
# desc: Save a contact for WhatsApp (add contact mom 9876543210)
# category: social
# usage: add contact <name> <number>
# rawargs: yes
import json, re
from _lib import args_text, data_dir, fail
words = args_text().split()
num = next((x for x in words if re.fullmatch(r"\+?\d[\d\-]{6,16}", x)), None)
name = " ".join(x for x in words if x != num).strip().lower()
if not num or not name:
    fail("Usage: add contact <name> <number with country code>   e.g. add contact mom 919876543210")
digits = re.sub(r"\D", "", num)
if len(digits) == 10:
    digits = "91" + digits; print("(10-digit number: assuming India, +91)")
if not 8 <= len(digits) <= 15:
    fail("Phone numbers need 8-15 digits including the country code.")
f = data_dir() / "contacts.json"
c = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
c[name] = digits
f.write_text(json.dumps(c, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"Saved {name}: +{digits}")
