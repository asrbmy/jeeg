# keywords: send whatsapp, whatsapp message, message, text someone, wa, send message, whatsapp number, chat with, msg
# desc: Start a WhatsApp message to a saved contact or number (send whatsapp to mom hello)
# category: social
# usage: send whatsapp <contact|number> <message>
# rawargs: yes
import json, re, urllib.parse
from _lib import args_text, data_dir, fail, open_url
words = args_text().split()
while words and words[0].lower() in {"message", "msg", "text", "to", "a", "the", "on", "whatsapp", "saying", "say"}:
    words.pop(0)
digits, msg_words = None, words
num = next((x for x in words if re.fullmatch(r"\+?\d[\d\s\-]{6,16}", x)), None)
if num:
    digits = re.sub(r"\D", "", num)
    if len(digits) == 10:
        digits = "91" + digits; print("(10-digit number: assuming India, +91)")
    msg_words = [x for x in words if x != num]
else:
    f = data_dir() / "contacts.json"
    contacts = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    low = [x.lower() for x in words]
    for n in range(min(3, len(words)), 0, -1):          # longest contact name first
        if " ".join(low[:n]) in contacts:
            digits = contacts[" ".join(low[:n])]; msg_words = words[n:]; break
if not digits:
    fail("Who to? Use a number (send whatsapp 919876543210 hello) or save a contact first: add contact mom 919876543210")
while msg_words and msg_words[0].lower() in {"saying", "say", "that", ":"}:
    msg_words.pop(0)
if not 8 <= len(digits) <= 15:
    fail("Phone numbers need 8-15 digits including the country code.")
msg = " ".join(msg_words)
open_url(f"https://wa.me/{digits}" + (f"?text={urllib.parse.quote(msg)}" if msg else ""))
print(f"Opened WhatsApp for +{digits} - press send there to deliver it.")
