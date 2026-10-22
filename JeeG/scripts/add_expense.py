# keywords: expense, spent, paid, add expense, record expense, log expense, cost
# desc: Record spending (spent 450 on groceries, add expense 200 food lunch)
# category: money
# usage: add expense <amount> <category> [note]
# rawargs: yes
# priority: 1
import csv, re, time
from _lib import args_text, data_dir, fail
t = args_text()
m = re.search(r"(?<![\w.])(\d[\d,]*(?:\.\d{1,2})?)(?![\w])", t)
if not m:
    fail("Usage: add expense <amount> <category> [note]   e.g. add expense 450 groceries milk and eggs")
amount = float(m.group(1).replace(",", ""))
if amount <= 0 or amount > 1e9:
    fail("Amount must be positive.")
rest = (t[:m.start()] + " " + t[m.end():])
rest = re.sub(r"\b(?:rs\.?|inr|rupees?|usd|dollars?|spent|paid|on|for|in|at|expense|add|record|log)\b|[₹$]", " ", rest, flags=re.I).split()
cat = rest[0].lower() if rest else "misc"
note = " ".join(rest[1:])
f = data_dir() / "expenses.csv"
new = not f.exists()
with open(f, "a", newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh)
    if new: wr.writerow(["date", "amount", "category", "note"])
    wr.writerow([time.strftime("%Y-%m-%d"), f"{amount:.2f}", cat, note])
print(f"Recorded {amount:,.2f} under '{cat}'" + (f" ({note})" if note else "") + ".")
try:
    import datetime
    from _store import load
    from _money import inr
    lim = load("budgets.json", {}).get(cat)
    if lim:
        mo, tot = time.strftime("%Y-%m"), 0.0
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if r["date"].startswith(mo) and r["category"] == cat: tot += float(r["amount"])
        if tot > lim: print(f"  Warning: over your {cat} budget: {inr(tot)} of {inr(lim)} this month.")
        elif tot >= 0.8 * lim: print(f"  Heads up: {int(100 * tot / lim)}% of your {cat} budget used ({inr(tot)} of {inr(lim)}).")
except Exception:
    pass
