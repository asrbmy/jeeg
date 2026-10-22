# keywords: countdown, add countdown, days left until, days until, event countdown, how many days until
# desc: Count the days to an event (add countdown exam 12 dec 2026)
# category: reminders
# usage: add countdown <event> <date>
# rawargs: full
# patterns: ^(?!.*\b(remove|delete|clear|stop|show|list|my)\b).*\bcount ?down\b
# priority: 1
import datetime, re
from _lib import args_text, fail
from _dates import parse_date
from _store import load, save
t = args_text()
t = re.sub(r"^\s*(please\s+)?(add|set|new|create|start)?\s*(a\s+)?count ?down\s*(for|to|until)?\s*", "", t, flags=re.I)
words = t.split(); d = None; name = ""
for i in range(len(words)):                       # the longest tail that reads as a date
    d = parse_date(" ".join(words[i:]))
    if d: name = " ".join(words[:i]).strip(" ,-").lower(); break
if not d or not name: fail("Usage: add countdown <event> <date>   e.g. add countdown exam 12 dec 2026")
if d < datetime.date.today(): fail("That date has already passed.")
c = load("countdowns.json", []); c = [x for x in c if x["name"] != name]; c.append({"name": name, "date": d.isoformat()}); save("countdowns.json", c)
print(f"{name}: {d:%d %b %Y}, {(d - datetime.date.today()).days} day(s) to go.")
