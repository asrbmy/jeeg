# keywords: upcoming birthdays, birthdays, birthday list, whose birthday, next birthday, birthdays soon, show birthdays
# desc: Show birthdays in the next 60 days
# category: birthdays
import datetime
from _store import load
b = load("birthdays.json", {})
today = datetime.date.today()
rows = []
for name, v in b.items():
    m, d = int(v["date"][:2]), int(v["date"][3:])
    try:
        nxt = datetime.date(today.year, m, d)
    except ValueError:
        nxt = datetime.date(today.year, 3, 1)               # Feb 29 in a non-leap year
    if nxt < today:
        nxt = nxt.replace(year=today.year + 1) if not (m == 2 and d == 29) else datetime.date(today.year + 1, 3, 1)
    rows.append(((nxt - today).days, name, nxt, v.get("year")))
rows.sort()
shown = [r for r in rows if r[0] <= 60]
if not b:
    print("No birthdays saved. Try: add birthday mom 14 aug")
elif not shown:
    print("No birthdays in the next 60 days.")
for days, name, nxt, yr in shown:
    age = f"  (turns {nxt.year - yr})" if yr else ""
    print(f"  {nxt:%a %d %b}  {'TODAY' if days == 0 else f'in {days} days':<12} {name.title()}{age}")
