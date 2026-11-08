# keywords: salary breakup, take home pay, net salary, in hand salary, gross to net, salary after tax, paycheck
# desc: Take-home pay from gross salary (salary breakup 5000 a month tax 20 pension 5; salary 60000 a year tax 22)
# category: money
# usage: salary breakup <amount> [a month|a year] [tax %] [pension %] [insurance %] [other <amount>]
# rawargs: yes
# patterns: \bsalary\s+break\s*up\b ;; \b(take|in)[\s-]?home\s+(pay|salary)\b ;; \bgross\s+to\s+net\b ;; \bnet\s+salary\b
# priority: 2
import re
from _lib import args_text, fail
t = args_text().lower().replace(",", "")
def pct(word):
    m = re.search(r"(?:" + word + r")\D{0,12}?(\d+(?:\.\d+)?)\s*%?", t)
    return float(m.group(1)) if m else 0.0
m = re.search(r"(\d+(?:\.\d+)?)\s*(k|m)?\b", re.sub(r"\b(salary|breakup|take|home|pay|gross|net)\b", " ", t))
if not m:
    fail("Usage: salary breakup 5000 a month tax 20 pension 5   (percentages for tax, pension, insurance; add 'other 100' for fixed monthly costs)")
gross = float(m.group(1)) * {"k": 1e3, "m": 1e6}.get(m.group(2) or "", 1)
yearly = bool(re.search(r"\b(year|yearly|annual|annum|pa|ctc)\b", t))
monthly = gross / 12 if yearly else gross
tax, pension, insurance = pct(r"tax"), pct(r"pension|retirement|pf|401k"), pct(r"insurance|health")
other = 0.0
o = re.search(r"other\D{0,6}(\d+(?:\.\d+)?)", t)
if o:
    other = float(o.group(1))
if not (0 < monthly < 1e12) or any(not 0 <= x < 100 for x in (tax, pension, insurance)) or tax + pension + insurance >= 100:
    fail("Check the numbers: percentages must be between 0 and 100 in total.")
rows = [("Gross pay", monthly), (f"Income tax ({tax:g}%)", -monthly * tax / 100), (f"Pension / retirement ({pension:g}%)", -monthly * pension / 100),
        (f"Insurance ({insurance:g}%)", -monthly * insurance / 100), ("Other deductions", -other)]
net = sum(v for _, v in rows)
print("Per month" + (f"  (from {gross:,.2f} a year)" if yearly else ""))
for n, v in rows:
    if v or n == "Gross pay":
        print(f"  {n:<34} {v:>14,.2f}")
print(f"  {'Take-home':<34} {net:>14,.2f}   ({net / monthly * 100:.1f}% of gross; {net * 12:,.2f} a year)")
print("  Rates are the ones you gave. This is an estimate, not payroll advice.")
