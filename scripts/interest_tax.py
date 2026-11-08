# keywords: interest tax, tax on interest, savings interest tax, deposit interest tax, withholding tax interest, after tax interest
# desc: Tax on interest earned (interest tax deposit 10000 rate 5 tax 25; interest tax 800 tax 15)
# category: money
# usage: interest tax <interest> tax <rate %>   |   interest tax deposit <amount> rate <%> tax <%>
# rawargs: full
# patterns: \btax\s+on\s+(savings\s+|fd\s+|deposit\s+)?interest\b ;; \binterest\s+tax\b ;; \bafter[\s-]tax\s+interest\b
# priority: 2
import re
from _lib import args_text, fail
t = re.sub(r"^\s*(?:what\s+is\s+the\s+|calculate\s+|work\s+out\s+)?(?:(?:the\s+)?tax\s+on\s+(?:savings\s+|fd\s+|deposit\s+)?interest|(?:savings\s+|deposit\s+|after[\s-]tax\s+)?interest\s+tax)", " ", args_text().lower().replace(",", ""))
def pick(pat):
    m = re.search(pat, t)
    return float(m.group(1)) if m else None
tax = pick(r"tax\D{0,6}(\d+(?:\.\d+)?)\s*%?")
dep, rate = pick(r"(?:deposit|balance|principal)\D{0,6}(\d+(?:\.\d+)?)"), pick(r"(?:rate|at)\D{0,6}(\d+(?:\.\d+)?)\s*%?")
if dep and rate:
    interest = dep * rate / 100
else:
    t2 = re.sub(r"tax\D{0,6}\d+(?:\.\d+)?\s*%?", " ", t)
    m = re.search(r"(\d+(?:\.\d+)?)", t2)
    interest = float(m.group(1)) if m else None
if interest is None or tax is None or not (0 <= tax < 100) or interest < 0:
    fail("Usage: interest tax 10000 tax 25      (interest earned in a year, and your tax rate)\n"
         "   or: interest tax deposit 200000 rate 5 tax 25")
cut = interest * tax / 100
print(f"Interest earned : {interest:,.2f}")
print(f"Tax at {tax:g}%     : {cut:,.2f}")
print(f"You keep        : {interest - cut:,.2f}" + (f"   (after-tax rate {rate * (1 - tax / 100):.2f}%)" if dep and rate else ""))
