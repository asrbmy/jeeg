# keywords: notify due, what is due, due today, due soon, check due, anything due, remind due, due items
# desc: Pop up a notification for what is due: birthdays, bills, countdowns, medicine (what is due, notify due)
# category: reminders
# usage: notify due
# patterns: \bwhat('s| is)\s+due\b ;; \bnotify\s+(me\s+)?(what('s| is)\s+)?due\b ;; \banything\s+due\b
# priority: 1
import datetime
from _lib import fail
from _store import load
from _time import alert
today = datetime.date.today()
items = []
def days_to(m, d):
    try: x = datetime.date(today.year, m, d)
    except ValueError: x = datetime.date(today.year, 3, 1)
    if x < today: x = x.replace(year=today.year + 1) if not (m == 2 and d == 29) else datetime.date(today.year + 1, 3, 1)
    return (x - today).days
for n, v in load("birthdays.json", {}).items():
    k = days_to(int(v["date"][:2]), int(v["date"][3:5]))
    if k <= 1: items.append(f"Birthday {'today' if k == 0 else 'tomorrow'}: {n}")
for n, v in load("bills.json", {}).items():
    try: k = days_to(today.month, int(v["day"]))
    except (KeyError, ValueError, TypeError): continue
    if k <= 3: items.append(f"Bill {'today' if k == 0 else 'in ' + str(k) + ' day(s)'}: {n}")
for c in load("countdowns.json", []):
    try: k = (datetime.date.fromisoformat(c["date"]) - today).days
    except (KeyError, ValueError): continue
    if 0 <= k <= 3: items.append(f"{c['name']}: {'today' if k == 0 else str(k) + ' day(s) to go'}")
try:
    from _dues import due_soon
    for store, label, within in (("warranties.json", "Warranty ends", 14), ("vehicle_dues.json", "Vehicle due", 14), ("vaccines.json", "Vaccine due", 7)):
        for n, k in due_soon(store, within):
            items.append(f"{label}: {n} " + ("(overdue)" if k < 0 else "today" if k == 0 else f"in {k} day(s)"))
except Exception:
    pass
now = datetime.datetime.now().strftime("%H:%M")
for n, v in load("medicines.json", {}).items():
    miss = [x for x in v["times"] if x <= now and x not in v["taken"].get(today.isoformat(), [])]
    if miss: items.append(f"Medicine not ticked: {n} ({', '.join(miss)})")
if not items:
    print("Nothing due today or in the next few days.")
    raise SystemExit(0)
for i in items: print("  " + i)
alert("JeeG: due", "; ".join(items)[:200])
