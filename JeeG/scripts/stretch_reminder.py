# keywords: stretch, stand up, posture, move, exercise break, walk, sitting
# desc: Remind you to stand up and stretch every 45 minutes
# category: reminders
# usage: stretch reminder [minutes]
import re
from _lib import args_text, fail
from _time import load_reminders, start_worker
m = re.search(r"\d+(?:\.\d+)?", args_text())
mins = float(m.group()) if m else 45
if not 1 <= mins <= 600:
    fail("Choose between 1 and 600 minutes.")
desc = "every {:g} min: stretch".format(mins)
if any(i["desc"] == desc for i in load_reminders()):
    fail("That reminder is already running. (stop with: stop reminders)")
start_worker("repeat", mins * 60, 'Stand up and stretch for a minute.', desc)
print(f"OK - stretch reminder every {mins:g} minutes. Stop with: stop reminders")
