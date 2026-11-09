# keywords: spending forecast, expense forecast, will i overspend, month end spending, projected spending, predict spending, budget forecast, end of month spending
# desc: Predict this month's total spending from your pace so far, against your budgets (spending forecast).
# category: money
# usage: spending forecast
# patterns: \b(spending|expense|expenses)\s+forecast\b ;; \bwill\s+i\s+overspend\b ;; \b(predict|project(ed)?)\s+(my\s+)?spending\b ;; \bmonth\s+end\s+spending\b
# priority: 2
import csv, datetime, statistics
from collections import defaultdict
from _lib import data_dir
from _store import load
from _money import inr
def read_expenses():
    f = data_dir() / "expenses.csv"
    rows = []
    if not f.exists():
        return rows
    with open(f, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            try:
                d = datetime.date.fromisoformat((r.get("date") or "")[:10])
                a = float(r.get("amount") or 0)
            except ValueError:
                continue
            if a > 0:
                rows.append((d, a, (r.get("category") or "misc").strip().lower(), (r.get("note") or "").strip()))
    return rows
def month_key(d): return d.year * 12 + d.month - 1
def label(k): return f"{k // 12}-{k % 12 + 1:02d}"

rows = read_expenses()
today = datetime.date.today(); cur = month_key(today)
dim = (datetime.date(today.year + (today.month == 12), today.month % 12 + 1, 1) - datetime.timedelta(days=1)).day
mine = [(d, a, c) for d, a, c, _ in rows if month_key(d) == cur]
if not mine:
    print("Nothing spent yet this month, so there is nothing to project."); raise SystemExit(0)
spent = sum(a for _, a, _ in mine)
day = today.day
proj = spent / day * dim
print(f"Day {day} of {dim}: spent {inr(spent)}")
print(f"At this pace the month ends near {inr(proj)}  (about {inr(spent / day)} a day; {inr(proj - spent)} still to come)")
# a steadier estimate: blend with the average of the last 3 full months when there is history
past = defaultdict(float)
for d, a, c, _ in rows:
    k = month_key(d)
    if cur - 3 <= k < cur: past[k] += a
if len(past) >= 2:
    avg = sum(past.values()) / len(past)
    print(f"Your average full month lately is {inr(avg)}" + (f"; this month is on course to be {100 * (proj - avg) / avg:+.0f}% vs that" if avg else ""))
cats = defaultdict(float)
for _, a, c in mine: cats[c] += a
b = load("budgets.json", {})
if b:
    print("Against your budgets (projected):")
    for c, lim in sorted(b.items()):
        p = cats.get(c, 0) / day * dim
        flag = "OVER" if p > lim else ("close" if p > 0.9 * lim else "ok")
        print(f"  {c:<14} {inr(p):>14} of {inr(lim):<14} {flag}")
    over = [c for c, lim in b.items() if cats.get(c, 0) / day * dim > lim]
    if over:
        print("Likely to go over: " + ", ".join(over))
else:
    print("Set limits to compare with:  set budget food 5000")
if day < 5:
    print("(Only a few days of data: treat this as a rough guess.)")
