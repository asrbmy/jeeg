# keywords: eye, eyes, eye break, eye strain, rest eyes, screen break
# desc: 20-20-20 eye break reminder every 20 minutes
# category: reminders
# usage: eye break [minutes]
import re
from _lib import args_text, fail
from _time import load_reminders, start_worker
m = re.search(r"\d+(?:\.\d+)?", args_text())
mins = float(m.group()) if m else 20
if not 1 <= mins <= 600:
    fail("Choose between 1 and 600 minutes.")
desc = "every {:g} min: eye break".format(mins)
if any(i["desc"] == desc for i in load_reminders()):
    fail("That reminder is already running. (stop with: stop reminders)")
start_worker("repeat", mins * 60, 'Look at something 20 feet away for 20 seconds.', desc)
print(f"OK - eye break reminder every {mins:g} minutes. Stop with: stop reminders")
