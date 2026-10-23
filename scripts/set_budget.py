# keywords: set budget, budget for, monthly budget, spending limit, limit spending, budget limit
# desc: Set a monthly spending limit for a category (set budget food 5000)
# category: money
# usage: set budget <category> <amount>
# rawargs: yes
# priority: 1
import re
from _lib import args_text, fail
from _store import load, save
from _money import inr
t = args_text()
m = re.search(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(?![\w])", t)
if not m: fail("Usage: set budget <category> <amount>   e.g. set budget food 5000")
amt = float(m.group(1).replace(",", ""))
rest = re.sub(r"\b(set|budget|for|a|monthly|limit|spending|of|rs|inr|rupees?|my|on|at)\b|[₹]", " ", t[:m.start()] + " " + t[m.end():], flags=re.I).split()
cat = rest[0].lower() if rest else ""
if not cat or amt <= 0: fail("Usage: set budget <category> <amount>   e.g. set budget food 5000")
b = load("budgets.json", {}); b[cat] = amt; save("budgets.json", b)
print(f"Budget for {cat}: {inr(amt)} per month.")
