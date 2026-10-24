# keywords: lend, lent, lend money, i lent, gave loan to, money lent, owes me
# desc: Note money you lent to someone (lend 500 to ravi for lunch)
# category: money
# usage: lend <amount> to <name> [note]
# rawargs: yes
# private: yes
# patterns: ^\s*lend\b ;; \bi\s+lent\b ;; \bgave\s+(a\s+)?loan\s+to\b
# priority: 2
import re, time
from _lib import args_text, fail
from _store import load, save
t = args_text()
m = re.search(r"(?<![\w.])(\d[\d,]*(?:\.\d{1,2})?)(?![\w])", t)
if not m: fail("Usage: lend <amount> to <name> [note]   e.g. lend 500 to ravi for lunch")
amt = float(m.group(1).replace(",", ""))
rest = (t[:m.start()] + " " + t[m.end():])
rest = re.sub(r"\b(?:lend|lent|i|rs\.?|inr|rupees?|money|gave|loan|to|for|a|the)\b|[₹$]", " ", rest, flags=re.I).split()
if not rest or not 0 < amt <= 1e9: fail("Usage: lend <amount> to <name> [note]   e.g. lend 500 to ravi for lunch")
name, note = rest[0].lower()[:30], " ".join(rest[1:])[:60]
led = load("ledger.json", {})
p = led.setdefault(name, {"balance": 0.0, "log": []})
p["balance"] = round(p["balance"] + amt, 2); p["log"] = (p["log"] + [[time.strftime("%Y-%m-%d"), amt, note]])[-50:]
save("ledger.json", led)
b = p["balance"]
print(f"Noted: {name} owes you {amt:,.2f}. " + (f"Total {name} owes you: {b:,.2f}." if b > 0 else f"You now owe {name} {-b:,.2f}." if b < 0 else "All settled."))
