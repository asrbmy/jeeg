# keywords: show timetable, my timetable, weekly schedule, class schedule, show classes, list classes, time table, weekly classes
# desc: Show your weekly timetable
# category: study
from _store import load
tt = load("timetable.json", [])
if not tt: print("No classes yet. Example:  add class maths mon 9:00")
D = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
for d in range(7):
    row = [x for x in tt if x["day"] == d]
    if row: print(f"{D[d]:<10}" + ",  ".join(f"{x['time']} {x['name'].title()}" for x in row))
