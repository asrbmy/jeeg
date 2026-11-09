# keywords: spending trends, expense trends, spending history, monthly spending, spending over time, where is my money going, spending comparison, expenses by month
# desc: Month-by-month spending, and which categories grew or shrank (spending trends).
# category: money
# usage: spending trends
# patterns: \b(spending|expense|expenses)\s+trends?\b ;; \bspending\s+(history|over\s+time|comparison)\b ;; \bwhere\s+is\s+my\s+money\s+going\b
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
if not rows:
    print("No expenses yet. Add some:  spent 450 on groceries"); raise SystemExit(0)
today = datetime.date.today(); cur = month_key(today)
tot = defaultdict(float); cat = defaultdict(lambda: defaultdict(float))
for d, a, c, _ in rows:
    k = month_key(d); tot[k] += a; cat[k][c] += a
ks = [k for k in range(cur - 5, cur + 1)]
mx = max(tot.get(k, 0) for k in ks) or 1
print("Last 6 months")
for k in ks:
    v = tot.get(k, 0)
    print(f"  {label(k)}  {'#' * int(30 * v / mx):<30} {inr(v)}" + ("  (so far)" if k == cur else ""))
past = [tot[k] for k in ks[:-1] if tot.get(k)]
if past:
    avg = sum(past) / len(past)
    print(f"Average of the full months: {inr(avg)}")
prev = cur - 1
if tot.get(prev) and tot.get(cur) is not None:
    dim = (datetime.date(today.year + (today.month == 12), today.month % 12 + 1, 1) - datetime.timedelta(days=1)).day
    same_point = sum(a for d, a, c, _ in rows if month_key(d) == prev and d.day <= today.day)
    if same_point:
        ch = 100 * (tot[cur] - same_point) / same_point
        print(f"This month so far {inr(tot[cur])} vs {inr(same_point)} by the same day last month ({ch:+.0f}%)")
    catp = defaultdict(float)
    for d, a, c, _ in rows:
        if month_key(d) == prev and d.day <= today.day: catp[c] += a
    cats = set(cat[cur]) | set(catp); diffs = []
    for c in cats:
        a, b = cat[cur].get(c, 0), catp.get(c, 0)
        diffs.append((a - b, c, a, b))
    diffs.sort(reverse=True)
    up = [x for x in diffs if x[0] > 0][:3]; down = [x for x in reversed(diffs) if x[0] < 0][:3]
    if up:
        print("Up vs the same days last month:   " + ", ".join(f"{c} +{inr(dv)}" for dv, c, a, b in up))
    if down:
        print("Down vs the same days last month: " + ", ".join(f"{c} {inr(dv)}" for dv, c, a, b in down))
top = sorted(cat[cur].items(), key=lambda x: -x[1])[:3]
if top:
    print("Biggest this month: " + ", ".join(f"{c} {inr(v)}" for c, v in top))
