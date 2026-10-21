# keywords: birthday, add birthday, save birthday, remember birthday, anniversary, born on, new birthday
# desc: Save a birthday (add birthday mom 14 aug, add birthday raj 3 march 1999)
# category: birthdays
# usage: add birthday <name> <date>
# rawargs: yes
import re, datetime
from _lib import args_text, fail
from _store import load, save
from _dates import parse_date
t = args_text()
ym = re.search(r"\b(19|20)\d{2}\b", t)
d = parse_date(re.sub(r"\b(birthday|add|save|remember)\b", " ", t, flags=re.I)) if t else None
if not d:
    for k in range(len(t.split()) - 1, 0, -1):          # find the longest tail that parses as a date
        cand = parse_date(" ".join(t.split()[-k:]))
        if cand: d = cand; name_words = t.split()[:-k]; break
    else:
        name_words = []
    if not d or not name_words:
        fail("Usage: add birthday <name> <date>   e.g. add birthday mom 14 aug")
else:
    fail("Put the name first: add birthday mom 14 aug")
name = " ".join(name_words).lower().strip()
b = load("birthdays.json", {})
b[name] = {"date": d.strftime("%m-%d"), "year": int(ym.group()) if ym else None}
save("birthdays.json", b)
print(f"Saved {name.title()}: {d:%d %B}" + (f" {ym.group()}" if ym else ""))
