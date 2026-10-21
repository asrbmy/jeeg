# keywords: water, drink water, hydrate, hydration, drink, stay hydrated, water break
# desc: Remind you to drink water every 30 minutes
# category: reminders
# usage: water reminder [minutes]
import re
from _lib import args_text, fail
from _time import load_reminders, start_worker
m = re.search(r"\d+(?:\.\d+)?", args_text())
mins = float(m.group()) if m else 30
if not 1 <= mins <= 600:
    fail("Choose between 1 and 600 minutes.")
desc = "every {:g} min: water".format(mins)
if any(i["desc"] == desc for i in load_reminders()):
    fail("That reminder is already running. (stop with: stop reminders)")
start_worker("repeat", mins * 60, 'Time to drink some water!', desc)
print(f"OK - water reminder every {mins:g} minutes. Stop with: stop reminders")
