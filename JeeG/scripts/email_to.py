# keywords: email to, mail to, email mom, email address of
# desc: Start an email to a saved contact or address (email mom about dinner)
# category: email
# usage: email <contact|address> [about <subject>]
# rawargs: yes
# patterns: ^\s*(please\s+)?(email|mail)\s+\S+
# priority: 1
import json, re, urllib.parse
from _lib import args_text, data_dir, fail, open_url
words = args_text().split()
while words and words[0].lower() in {"email", "mail", "write", "send", "to", "a", "an", "compose", "new"}:
    words.pop(0)
f = data_dir() / "emails.json"
em = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
to, rest = None, words
if words and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", words[0]):
    to, rest = words[0], words[1:]
else:
    low = [x.lower() for x in words]
    for n in range(min(3, len(words)), 0, -1):
        if " ".join(low[:n]) in em:
            to, rest = em[" ".join(low[:n])], words[n:]; break
if not to: fail("Who to? Save an address first: add email mom mom@example.com   (then: email mom about dinner)")
while rest and rest[0].lower() in {"about", "regarding", "re", "subject", "saying", "that"}: rest.pop(0)
q = urllib.parse.urlencode({"view": "cm", "fs": 1, "to": to, "su": " ".join(rest)}, quote_via=urllib.parse.quote)
open_url("https://mail.google.com/mail/?" + q)
print(f"Opened a draft to {to}.")
