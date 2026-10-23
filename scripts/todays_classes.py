# keywords: todays classes, classes today, tomorrow classes, tomorrows classes, what classes do i have, class today, schedule today, next class, lectures today
# desc: Classes you have today or tomorrow (todays classes, tomorrows classes)
# category: study
# usage: todays classes | tomorrows classes
# rawargs: yes
import datetime, re
from _lib import args_text
from _store import load
tt = load("timetable.json", [])
tomorrow = bool(re.search(r"\btomorrow", args_text(), re.I))
d = datetime.date.today() + datetime.timedelta(days=1 if tomorrow else 0)
row = [x for x in tt if x["day"] == d.weekday()]
now = datetime.datetime.now().strftime("%H:%M")
print(f"{'Tomorrow' if tomorrow else 'Today'} ({d:%A}):")
if not row: print("  no classes")
for x in row:
    print(f"  {x['time']}  {x['name'].title()}" + ("   <- next" if not tomorrow and x["time"] >= now and x is next((y for y in row if y['time'] >= now), None) else ""))
