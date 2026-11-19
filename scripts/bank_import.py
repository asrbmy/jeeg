# keywords: import bank, bank statement, bank csv, import statement, import transactions
# desc: Import a bank statement CSV into your expenses (import bank statement.csv); guesses categories, skips duplicates
# category: money
# usage: import bank <file.csv>
# rawargs: full
# patterns: \bimport\s+(my\s+)?(bank|statement|transactions)\b
# priority: 4
import csv, re
from pathlib import Path
from _lib import args_text, data_dir, fail
from _dates import parse_date
t = re.sub(r"^\s*import\s+(?:my\s+)?(?:bank\s+)?(?:statement|transactions|csv)?\s*", "", args_text(), flags=re.I).strip().strip("\"'")
p = Path(t).expanduser()
if not t or not p.is_file(): fail("Usage: import bank <file.csv>   (the path of the CSV you downloaded from your bank)")
if p.stat().st_size > 20_000_000: fail("That file is too big (limit 20 MB).")
CATS = {"food": "swiggy zomato restaurant cafe pizza grocer bigbasket blinkit dmart", "transport": "uber ola fuel petrol metro irctc railway", "bills": "electric power water gas recharge broadband airtel jio", "shopping": "amazon flipkart myntra", "entertainment": "netflix spotify hotstar prime cinema"}
def guess(n):
    n = n.lower()
    for c, ws in CATS.items():
        if any(w in n for w in ws.split()): return c
    return "misc"
def num(x):
    x = re.sub(r"[^\d.]", "", x or ""); return float(x) if x.count(".") <= 1 and x else 0.0
text = p.read_text(encoding="utf-8-sig", errors="replace")
rows = list(csv.reader(text.splitlines()))
h = next((i for i, r in enumerate(rows[:30]) if any("date" in c.lower() for c in r) and len(r) >= 3), None)
if h is None: fail("I could not find a header row with a Date column.")
hd = [c.strip().lower() for c in rows[h]]
def col(*names): return next((i for i, c in enumerate(hd) if any(n in c for n in names)), None)
cd, cn, cdr, ca = col("date"), col("narration", "description", "particulars", "details", "remarks"), col("debit", "withdrawal", "dr"), col("amount")
if cd is None or (cdr is None and ca is None): fail("I need a Date column and a Debit/Withdrawal or Amount column.")
f = data_dir() / "expenses.csv"
seen = set()
if f.exists():
    for r in csv.DictReader(open(f, encoding="utf-8")): seen.add((r["date"], r["amount"], r["note"]))
new = not f.exists(); added = skipped = 0; total = 0.0
with open(f, "a", newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh)
    if new: wr.writerow(["date", "amount", "category", "note"])
    for r in rows[h + 1:]:
        if len(r) <= cd: continue
        d = parse_date(r[cd].strip())
        if not d: continue
        a = num(r[cdr]) if cdr is not None and len(r) > cdr else (-num(r[ca]) if ca is not None and r[ca].strip().startswith("-") else 0.0)
        if a <= 0: continue
        note = (r[cn].strip() if cn is not None and len(r) > cn else "")[:60]
        k = (d.isoformat(), f"{a:.2f}", note)
        if k in seen: skipped += 1; continue
        seen.add(k); wr.writerow([k[0], k[1], guess(note), note]); added += 1; total += a
print(f"Imported {added} spending row(s) ({total:,.2f} in all); skipped {skipped} duplicate(s). Look at them with:  budget report")
