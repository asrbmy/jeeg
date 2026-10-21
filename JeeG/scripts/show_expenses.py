# keywords: show expenses, list expenses, my expenses, spending list, expense list, expense history, where did i spend
# desc: List expenses (show expenses, show expenses food, show expenses last month)
# category: money
# usage: show expenses [category] [month]
# rawargs: yes
import csv
from _lib import args_text, data_dir
from _store import MONTHS, period
f = data_dir() / "expenses.csv"
rows = list(csv.DictReader(open(f, encoding="utf-8"))) if f.exists() else []
q = args_text().lower()
s, e, label = period(q)
words = [x for x in q.split() if x not in MONTHS and x not in ("last", "month", "this", "all", "today", "week", "year", "for", "in", "of", "my") and not x.isdigit()]
sel = [r for r in rows if (s is None or s.isoformat() <= r["date"] <= e.isoformat())
       and (not words or any(w in (r["category"] + " " + r["note"]).lower() for w in words))]
if not sel:
    print(f"No expenses found for {label}.")
for r in sel[-25:]:
    print(f"{r['date']}  {float(r['amount']):>10,.2f}  {r['category']:<12} {r['note']}")
print(f"-- {len(sel)} item(s), total {sum(float(r['amount']) for r in sel):,.2f}  ({label})")
