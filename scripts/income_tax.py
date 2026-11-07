# keywords: income tax, tax calculator, tax on salary, new regime, old regime, itr tax, how much tax
# desc: Income tax, new vs old regime (income tax 12 lakh; income tax 18 lakh deductions 2 lakh)
# category: money
# usage: income tax <income> [deductions <amount>]
# rawargs: yes
# patterns: \bincome\s+tax\b ;; \b(new|old)\s+(tax\s+)?regime\b ;; \bhow\s+much\s+tax\b ;; \btax\s+(calculator|on\s+salary)\b
# priority: 2
import re
from _lib import args_text, fail
from _money import inr
t = args_text().lower().replace(",", "")
m = re.search(r"(\d+(?:\.\d+)?)\s*(lakhs?|lacs?|l|crores?|cr|k)?\b", t)
if not m:
    fail("Usage: income tax 12 lakh   (add 'deductions 2 lakh' for the old regime: 80C, 80D, home loan ...)")
mult = {"lakh": 1e5, "lakhs": 1e5, "lac": 1e5, "lacs": 1e5, "l": 1e5, "crore": 1e7, "crores": 1e7, "cr": 1e7, "k": 1e3}
def amt(x, u): return float(x) * mult.get(u or "", 1)
inc = amt(m.group(1), m.group(2))
d = re.search(r"deductions?\s*(\d+(?:\.\d+)?)\s*(lakhs?|lacs?|l|k)?\b", t)
ded = amt(d.group(1), d.group(2)) if d else 0.0
if inc <= 0 or inc > 1e10:
    fail("Give a yearly income, for example: income tax 12 lakh")
def slab(x, rows):
    tax, prev = 0.0, 0.0
    for upto, rate in rows:
        if x > prev:
            tax += (min(x, upto) - prev) * rate
        prev = upto
    return tax
INF = float("inf")
new_rows = [(4e5, 0), (8e5, .05), (12e5, .10), (16e5, .15), (20e5, .20), (24e5, .25), (INF, .30)]
old_rows = [(2.5e5, 0), (5e5, .05), (10e5, .20), (INF, .30)]
nt_inc = max(0, inc - 75000)
nt = slab(nt_inc, new_rows)
if nt_inc <= 12e5:
    nt = 0.0                                          # section 87A rebate (new regime)
elif nt > nt_inc - 12e5:
    nt = nt_inc - 12e5                                # marginal relief just above 12 lakh
ot_inc = max(0, inc - 50000 - ded)
ot = slab(ot_inc, old_rows)
if ot_inc <= 5e5:
    ot = 0.0
nt *= 1.04
ot *= 1.04
print(f"Yearly income {inr(inc)}" + (f", deductions {inr(ded)}" if ded else ""))
print(f"  New regime : tax {inr(nt)}  (taxable {inr(nt_inc)}, standard deduction 75,000)")
print(f"  Old regime : tax {inr(ot)}  (taxable {inr(ot_inc)}, standard deduction 50,000)")
better = "New" if nt <= ot else "Old"
print(f"  {better} regime is cheaper by {inr(abs(nt - ot))}. Monthly tax: {inr(min(nt, ot) / 12)}")
print("  Salaried slabs of FY 2025-26 with 4% cess; no surcharge. A guide only - check the latest rules or ask a CA.")
