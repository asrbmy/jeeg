# keywords: gas cylinder, lpg cylinder, cylinder changed, cylinder refill, cylinder due, cooking gas, when will gas run out
# desc: Track gas cylinder changes and when the next one is due (cylinder changed; cylinder; cylinder history)
# category: home
# usage: cylinder changed [date] | cylinder | cylinder remove
# rawargs: full
# private: yes
# patterns: \b(gas|lpg)\s+(cylinder|refill|due)\b ;; \bcylinder\s+(changed|due|history|remove|status)?\b ;; \bwhen\s+will\s+(the\s+)?gas\s+run\s+out\b
# priority: 3
import datetime, re
from _lib import args_text, fail
from _store import load, save
from _dates import parse_past_date as parse_date
low = args_text().lower()
data = load("gas_cylinder.json", [])
today = datetime.date.today()
if re.search(r"\b(changed|new|replaced|swapped|refill(ed)?|delivered|installed|started)\b", low):
    d = today
    rest = re.sub(r"\b(gas|lpg|cylinder|changed|new|replaced|swapped|refilled?|delivered|installed|started|on|today)\b", " ", low).strip()
    if rest:
        d = parse_date(rest)
        if d is None:
            fail("I could not read that date. Try:  cylinder changed 12 oct   or just  cylinder changed")
    if d > today:
        fail("That date is in the future.")
    if d.isoformat() in data:
        fail(f"Already recorded for {d}.")
    data = sorted(data + [d.isoformat()])[-60:]
    save("gas_cylinder.json", data)
    print(f"Recorded a new cylinder on {d:%d %b %Y}.")
elif re.search(r"\bremove|undo|delete\b", low):
    if not data:
        fail("Nothing recorded.")
    gone = data.pop()
    save("gas_cylinder.json", data)
    print(f"Removed the last entry ({gone}).")
if not data:
    fail("No cylinder recorded yet. Say:  cylinder changed   (when you fit a new one)")
ds = [datetime.date.fromisoformat(x) for x in data]
gaps = [(b - a).days for a, b in zip(ds, ds[1:])]
print(f"Current cylinder fitted {ds[-1]:%d %b %Y} ({(today - ds[-1]).days} days ago).")
if gaps:
    avg = sum(gaps[-6:]) / len(gaps[-6:])
    due = ds[-1] + datetime.timedelta(days=round(avg))
    left = (due - today).days
    print(f"Each cylinder has lasted about {avg:.0f} days (from {len(gaps)} change(s)). Next one due around {due:%d %b %Y}" +
          (f" - in {left} day(s). Book a refill about 5 days before." if left >= 0 else f" - overdue by {-left} day(s)."))
else:
    print("Record one more change and JeeG will estimate how long a cylinder lasts.")
