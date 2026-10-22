# keywords: budgets, budget report, am i over budget, budget left, show budget, budget check, spending limits
# desc: Show this month's spending against your budgets (budget report)
# category: money
# usage: budget report
# patterns: \bbudgets?\b.*\b(status|report|left|check|summary)\b ;; \bam i over (my )?budget\b ;; ^\s*(show\s+)?(my\s+)?budgets?\s*$
# priority: 1
import csv, datetime
from _lib import data_dir
from _store import load
from _money import inr
b = load("budgets.json", {})
if not b: print("No budgets yet. Set one: set budget food 5000"); raise SystemExit(0)
spent = {}
f = data_dir() / "expenses.csv"
month = datetime.date.today().strftime("%Y-%m")
if f.exists():
    for r in csv.DictReader(open(f, encoding="utf-8")):
        try:
            if r["date"].startswith(month): spent[r["category"]] = spent.get(r["category"], 0) + float(r["amount"])
        except (KeyError, ValueError): pass
print(f"Budgets for {datetime.date.today():%B %Y}:")
for c, lim in sorted(b.items()):
    s = spent.get(c, 0); pct = int(100 * s / lim) if lim else 0
    flag = "  OVER" if s > lim else ("  close" if pct >= 80 else "")
    print(f"  {c:<14}{inr(s):>12} of {inr(lim):<12}{pct:>4}%{flag}")
other = {c: s for c, s in spent.items() if c not in b}
if other: print("  No budget set for: " + ", ".join(f"{c} ({inr(s)})" for c, s in sorted(other.items())))
