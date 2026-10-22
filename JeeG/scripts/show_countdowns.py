# keywords: show countdowns, my countdowns, days left, list countdowns, countdown list, how many days left
# desc: Show the days left for your events (show countdowns)
# category: reminders
# usage: show countdowns
# priority: 1
import datetime
from _store import load
c = sorted(load("countdowns.json", []), key=lambda x: x["date"])
if not c: print("No countdowns. Add one: add countdown exam 12 dec 2026"); raise SystemExit(0)
today = datetime.date.today()
for x in c:
    d = datetime.date.fromisoformat(x["date"]); n = (d - today).days
    print(f"  {x['name']:<22}{d:%d %b %Y}   " + ("today!" if n == 0 else f"{n} day(s) to go" if n > 0 else f"{-n} day(s) ago"))
