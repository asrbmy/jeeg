# keywords: ledger, who owes, who owes me, who do i owe, money owed, show ledger, dues list, balances
# desc: See who owes you and who you owe (ledger, who owes me, show ledger ravi)
# category: money
# usage: ledger [name]
# rawargs: full
# private: yes
# patterns: \bledger\b ;; \bwho\s+owes\b ;; \bwho\s+do\s+i\s+owe\b
# priority: 2
import re
from _lib import args_text, fail
from _store import load
t = args_text().lower()
led = {k: v for k, v in load("ledger.json", {}).items() if abs(v["balance"]) > 0.004}
who = re.sub(r"\b(show|ledger|who|owes|me|do|i|owe|money|owed|my|the|all|dues|list|balances|of|for)\b", " ", t).split()
if who:
    k = who[0]
    p = load("ledger.json", {}).get(k)
    if not p: fail(f"No record for '{k}'.")
    print(f"{k}: " + (f"owes you {p['balance']:,.2f}" if p["balance"] > 0 else f"you owe {-p['balance']:,.2f}" if p["balance"] < 0 else "settled"))
    for d, a, n in p["log"][-10:]:
        print(f"  {d}  {'+' if a > 0 else '-'}{abs(a):,.2f}  {n}")
    raise SystemExit(0)
if not led: fail("Nothing owed either way. Add one with: lend 500 to ravi   |   borrow 300 from asha")
owe_me = sorted(((k, v["balance"]) for k, v in led.items() if v["balance"] > 0), key=lambda x: -x[1])
i_owe = sorted(((k, -v["balance"]) for k, v in led.items() if v["balance"] < 0), key=lambda x: -x[1])
if owe_me:
    print(f"People who owe you ({sum(v for _, v in owe_me):,.2f} in all):")
    for k, v in owe_me: print(f"  {k:<18}{v:>12,.2f}")
if i_owe:
    print(f"You owe ({sum(v for _, v in i_owe):,.2f} in all):")
    for k, v in i_owe: print(f"  {k:<18}{v:>12,.2f}")
