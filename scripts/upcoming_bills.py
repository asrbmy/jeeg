# keywords: upcoming bills, bills due, what bills are due, show bills, due this week, my bills, pending bills, list bills, bills this month
# desc: Bills due soon (upcoming bills, upcoming bills 30)
# category: money
# usage: upcoming bills [days]
# rawargs: yes
import calendar, datetime, re
from _lib import args_text
from _store import load
b = load("bills.json", {})
m = re.search(r"\d+", args_text())
span = int(m.group()) if m else 10
today = datetime.date.today()
rows = []
for name, v in b.items():
    for add in (0, 1):                                  # this month and next
        y, mo = divmod(today.year * 12 + today.month - 1 + add, 12)
        d = datetime.date(y, mo + 1, min(v["day"], calendar.monthrange(y, mo + 1)[1]))
        if d >= today:
            rows.append((d, name, v.get("amount"))); break
rows.sort()
if not b: print("No bills saved. Example:  add bill electricity 15 1200")
else:
    shown = [r for r in rows if (r[0] - today).days <= span]
    for d, n, a in shown:
        left = (d - today).days
        print(f"  {d:%a %d %b}  {n.title():<22}{('Rs ' + format(a, ',.0f')) if a else '':>12}   " + ("TODAY" if left == 0 else f"in {left} day(s)"))
    if not shown: print(f"Nothing due in the next {span} days. (All bills: " + ", ".join(f"{n} on day {v['day']}" for n, v in b.items()) + ")")
