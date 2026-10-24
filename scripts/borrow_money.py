# keywords: borrow, borrowed, borrow money, i borrowed, i owe, took loan from, money borrowed
# desc: Note money you borrowed from someone (borrow 300 from asha)
# category: money
# usage: borrow <amount> from <name>
# rawargs: yes
# private: yes
# patterns: ^\s*borrow\b ;; \bi\s+borrowed\b ;; \btook\s+(a\s+)?loan\s+from\b
# priority: 2
import re, time
from _lib import args_text, fail
from _store import load, save
t = args_text()
m = re.search(r"(?<![\w.])(\d[\d,]*(?:\.\d{1,2})?)(?![\w])", t)
if not m: fail("Usage: borrow <amount> from <name>   e.g. borrow 300 from asha")
amt = float(m.group(1).replace(",", ""))
rest = (t[:m.start()] + " " + t[m.end():])
rest = re.sub(r"\b(?:borrow|borrowed|i|rs\.?|inr|rupees?|money|took|loan|from|for|a|the)\b|[₹$]", " ", rest, flags=re.I).split()
if not rest or not 0 < amt <= 1e9: fail("Usage: borrow <amount> from <name>   e.g. borrow 300 from asha")
name, note = rest[0].lower()[:30], " ".join(rest[1:])[:60]
led = load("ledger.json", {})
p = led.setdefault(name, {"balance": 0.0, "log": []})
p["balance"] = round(p["balance"] - amt, 2); p["log"] = (p["log"] + [[time.strftime("%Y-%m-%d"), -amt, note]])[-50:]
save("ledger.json", led)
b = p["balance"]
print(f"Noted: you owe {name} {amt:,.2f}. " + (f"Total you owe {name}: {-b:,.2f}." if b < 0 else f"{name} now owes you {b:,.2f}." if b > 0 else "All settled."))
