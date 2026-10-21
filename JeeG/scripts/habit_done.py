# keywords: habit, habit done, did, done today, completed, check in, tick, i did, workout done, log habit, habit tracker
# desc: Tick a habit for today (habit done gym)
# category: habits
# usage: habit done <name>
# rawargs: yes
# priority: 1
import datetime
from _lib import args_text, fail
from _store import load, save
name = " ".join(x for x in args_text().lower().split() if x not in ("today", "done", "habit")).strip()
if not name:
    fail("Usage: habit done <habit>   e.g. habit done gym")
h = load("habits.json", {})
today = datetime.date.today().isoformat()
days = h.setdefault(name, [])
if today in days:
    print(f"'{name}' is already ticked for today.")
else:
    days.append(today); days.sort(); save("habits.json", h)
    print(f"Ticked '{name}' for today.")
