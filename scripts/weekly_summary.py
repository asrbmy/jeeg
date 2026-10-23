# keywords: weekly summary, week summary, monthly summary, month summary, my week, weekly report, review my week, summary of my week, how was my week, progress report
# desc: One-page summary of your week or month: spending, habits, journal, to-dos, water and sleep (weekly summary, monthly summary)
# category: productivity
# usage: weekly summary | monthly summary
# rawargs: yes
# patterns: \bhow was my (week|month)\b ;; \b(weekly|monthly|week|month) (summary|report|review)\b
# priority: 1
import csv, datetime, json, re
from collections import Counter
from _lib import args_text, data_dir
from _money import inr
from _store import period, load
t = args_text().lower()
key = "month" if "month" in t else "week"
if re.search(r"\b(last month|today|all|year)\b", t): key = t
if key == "month":
    today = datetime.date.today(); start, end, label = today.replace(day=1), today, f"this month ({today:%B %Y})"
else:
    start, end, label = period(key if key != "week" else "week")
def inside(s):
    try: d = datetime.date.fromisoformat(s[:10])
    except ValueError: return False
    return (start is None or d >= start) and (end is None or d <= end)
d = data_dir()
print(f"=== Summary: {label} ===")
# spending
f = d / "expenses.csv"
if f.exists():
    tot, cat, n = 0.0, Counter(), 0
    with open(f, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if inside(r.get("date", "")):
                a = float(r.get("amount") or 0); tot += a; cat[r.get("category", "misc")] += a; n += 1
    print(f"Spending: {inr(tot)} in {n} item(s)" + (" - top: " + ", ".join(f"{c} {inr(v)}" for c, v in cat.most_common(3)) if n else ""))
else: print("Spending: no expenses recorded")
# habits
h = load("habits.json", {})
if h:
    span = ((end or datetime.date.today()) - start).days + 1 if start else None
    for name, days in sorted(h.items()):
        c = sum(1 for x in days if inside(x))
        print(f"Habit '{name}': {c}" + (f" of {span} days" if span else " day(s)"))
else: print("Habits: none tracked")
# journal
jf = d / "journal.txt"
jn = sum(1 for l in jf.read_text(encoding="utf-8").splitlines() if inside(l)) if jf.exists() else 0
print(f"Journal: {jn} entr{'y' if jn == 1 else 'ies'}")
# to-dos
tf = d / "todos.json"
if tf.exists():
    items = json.loads(tf.read_text(encoding="utf-8"))
    print(f"To-dos: {sum(1 for i in items if not i.get('done'))} open, {sum(1 for i in items if i.get('done'))} done in total")
# water and sleep
wt = load("water.json", {}); wd = {k: v for k, v in wt.items() if not k.startswith("_") and inside(k)}
if wd: print(f"Water: average {sum(wd.values()) / len(wd):,.0f} ml/day over {len(wd)} logged day(s)")
sl = load("sleep.json", {}); sd = {k: v for k, v in sl.items() if inside(k)}
if sd: print(f"Sleep: average {sum(sd.values()) / len(sd):.1f} h over {len(sd)} logged night(s)")
# birthdays
b = load("birthdays.json", {})
soon = []
for n, v in b.items():
    try: m, dd = map(int, v["date"].split("-")); nxt = datetime.date(datetime.date.today().year, m, dd)
    except (ValueError, KeyError): continue
    if nxt < datetime.date.today():
        try: nxt = nxt.replace(year=nxt.year + 1)
        except ValueError: continue
    if (nxt - datetime.date.today()).days <= 7: soon.append(f"{n.title()} ({nxt:%d %b})")
if soon: print("Birthdays in the next 7 days: " + ", ".join(soon))
