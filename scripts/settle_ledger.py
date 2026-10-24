# keywords: settle, settle up, settled, repaid, clear debt, debt cleared, clear ledger
# desc: Mark a debt as paid (settle ravi, settle ravi 200 for a part payment)
# category: money
# usage: settle <name> [amount]
# rawargs: yes
# private: yes
# patterns: ^\s*settle\b ;; \bsettle\s+up\b ;; \bpaid\s+me\s+back\b ;; \bi\s+paid\s+\w+\s+back\b
# priority: 2
import re, time
from _lib import args_text, fail
from _store import load, save
t = args_text().lower()
m = re.search(r"(?<![\w.])(\d[\d,]*(?:\.\d{1,2})?)(?![\w])", t)
part = float(m.group(1).replace(",", "")) if m else None
who = re.sub(r"(?<![\w.])\d[\d,]*(?:\.\d{1,2})?|\b(settle|settled|up|with|paid|back|repaid|clear|debt|cleared|ledger|rs|inr|to|by|from|me|i|has|have|the)\b", " ", t).split()
if not who: fail("Usage: settle <name> [amount]   e.g. settle ravi   |   settle ravi 200")
k = who[0]
led = load("ledger.json", {})
p = led.get(k)
if not p or abs(p["balance"]) < 0.005: fail(f"Nothing owed either way with '{k}'.")
b = p["balance"]
amt = abs(b) if part is None else min(part, abs(b))
if amt <= 0: fail("The amount must be above zero.")
p["balance"] = round(b - amt if b > 0 else b + amt, 2)
p["log"] = (p["log"] + [[time.strftime("%Y-%m-%d"), -amt if b > 0 else amt, "settled"]])[-50:]
if abs(p["balance"]) < 0.005: del led[k]
save("ledger.json", led)
left = abs(p["balance"])
print(f"Recorded {amt:,.2f} {'received from' if b > 0 else 'paid to'} {k}. " + ("All settled." if left < 0.005 else f"Still {'owed to you' if b > 0 else 'owed by you'}: {left:,.2f}."))
