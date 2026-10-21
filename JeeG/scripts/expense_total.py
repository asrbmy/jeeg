# keywords: expense total, total expenses, how much did i spend, spending summary, expense summary, monthly spending, budget summary, spending by category
# desc: Spending totals by category (expense total, expense total last month)
# category: money
# usage: expense total [month]
# rawargs: yes
# priority: 1
import csv
from collections import defaultdict
from _lib import args_text, data_dir
from _store import period
f = data_dir() / "expenses.csv"
rows = list(csv.DictReader(open(f, encoding="utf-8"))) if f.exists() else []
s, e, label = period(args_text())
by = defaultdict(float)
for r in rows:
    if s is None or s.isoformat() <= r["date"] <= e.isoformat():
        by[r["category"]] += float(r["amount"])
total = sum(by.values())
if not total:
    print(f"No expenses recorded for {label}."); raise SystemExit(0)
print(f"Spending - {label}")
for c, v in sorted(by.items(), key=lambda x: -x[1]):
    print(f"  {c:<14}{v:>12,.2f}  {'#' * max(1, round(30 * v / total))}  {100 * v / total:.0f}%")
print(f"  {'TOTAL':<14}{total:>12,.2f}")
