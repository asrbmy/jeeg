# keywords: spending anomalies, unusual expenses, odd spending, duplicate expenses, expense outliers, unusual spending, suspicious expenses, spending check
# desc: Find unusually large or possibly duplicated expenses (spending anomalies).
# category: money
# usage: spending anomalies
# patterns: \b(spending|expense|expenses)\s+(anomal\w+|outliers?)\b ;; \b(unusual|odd|suspicious|duplicate)\s+(spending|expenses?)\b
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
since = datetime.date.today() - datetime.timedelta(days=365)
rows = [r for r in rows if r[0] >= since]
if len(rows) < 8:
    print("Not enough history yet (needs at least 8 expenses in the last year)."); raise SystemExit(0)
bycat = defaultdict(list)
for r in rows: bycat[r[2]].append(r)
found = []
for c, rs in bycat.items():
    if len(rs) < 5: continue
    vals = [r[1] for r in rs]
    med = statistics.median(vals)
    mad = statistics.median([abs(v - med) for v in vals]) * 1.4826
    if mad == 0:
        mad = (statistics.pstdev(vals) or med * 0.1 or 1)
    for d, a, _, note in rs:
        z = (a - med) / mad
        if z >= 3.5 and a >= 1.8 * med:
            found.append((z, d, a, c, note, med))
found.sort(reverse=True)
seen = defaultdict(list)
for d, a, c, note in rows: seen[(d, a, c)].append(note)
dups = [(k, v) for k, v in seen.items() if len(v) > 1]
print(f"Checked {len(rows)} expenses from the last year in {len(bycat)} categories.")
if found:
    print("Unusually large (compared with your normal amount in that category):")
    for z, d, a, c, note, med in found[:8]:
        print(f"  {d}  {inr(a):>14}  {c:<12} usual about {inr(med)}" + (f"  - {note}" if note else ""))
if dups:
    print("Same amount, category and day more than once (possible double entry):")
    for (d, a, c), notes in sorted(dups, reverse=True)[:8]:
        print(f"  {d}  {inr(a):>14}  {c:<12} x{len(notes)}")
if not found and not dups:
    print("Nothing unusual found.")
else:
    print("These are hints, not errors. Use  show expenses  to look, and  undo expense  to remove the last one.")
