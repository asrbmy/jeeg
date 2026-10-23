# keywords: remove class, delete class, drop class, remove lesson, delete subject, cancel class
# desc: Remove a class from the timetable (remove class maths mon)
# category: study
# usage: remove class <subject> [day]
# rawargs: yes
import re
from _lib import args_text, fail
from _store import load, save
t = re.sub(r"\b(remove|delete|drop|class|lesson|the|cancel)\b", " ", args_text(), flags=re.I).lower().split()
if not t: fail("Usage: remove class <subject> [day]   e.g. remove class maths mon")
tt = load("timetable.json", [])
D = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
day = next((D[w[:3]] for w in t if w[:3] in D and len(w) <= 9), None)
words = [w for w in t if not (w[:3] in D and len(w) <= 9)]
keep = [x for x in tt if not (all(w in x["name"] for w in words) and (day is None or x["day"] == day))]
gone = len(tt) - len(keep)
if not gone: fail("No matching class found. See them with: show timetable")
save("timetable.json", keep)
print(f"Removed {gone} class(es).")
