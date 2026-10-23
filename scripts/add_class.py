# keywords: add class, add lesson, timetable add, new class, add subject, class schedule, add period, add lecture
# desc: Add a weekly class or lesson (add class maths mon 9:00, add class physics tue 2:30 pm room 4)
# category: study
# usage: add class <subject> <day> <time>
# rawargs: yes
import re
from _lib import args_text, fail
from _store import load, save
t = re.sub(r"\b(add|class|lesson|period|lecture|to|my|timetable)\b", " ", args_text(), flags=re.I)
DAYS = {"mon": 0, "monday": 0, "tue": 1, "tues": 1, "tuesday": 1, "wed": 2, "wednesday": 2, "thu": 3, "thur": 3, "thurs": 3, "thursday": 3,
        "fri": 4, "friday": 4, "sat": 5, "saturday": 5, "sun": 6, "sunday": 6}
dm = re.search(r"\b(" + "|".join(sorted(DAYS, key=len, reverse=True)) + r")\b", t, re.I)
tm = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", t, re.I)
if not dm or not tm: fail("Usage: add class <subject> <day> <time>   e.g. add class maths mon 9:00   or   add class physics tue 2:30 pm")
hh, mn, ap = int(tm.group(1)), int(tm.group(2) or 0), (tm.group(3) or "").lower()
if ap: hh = hh % 12 + (12 if ap == "pm" else 0)
if hh > 23 or mn > 59: fail("That is not a valid time.")
name = " ".join((t[:min(dm.start(), tm.start())] + " " + t[max(dm.end(), tm.end()):]).split()).strip() or "class"
if dm.start() < tm.start(): name = " ".join(t[:dm.start()].split()) or name
tt = load("timetable.json", [])
tt.append({"name": name.lower(), "day": DAYS[dm.group(1).lower()], "time": f"{hh:02d}:{mn:02d}"})
tt.sort(key=lambda x: (x["day"], x["time"]))
save("timetable.json", tt)
print(f"Added: {name.title()} on {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][DAYS[dm.group(1).lower()]]} at {hh:02d}:{mn:02d}")
