# keywords: compare loans, loan comparison, compare emi, which loan is cheaper, two loans, loan offers, loan vs loan, compare loan offers
# desc: Compare two loan offers side by side (compare loans 500000 8.5% 5y vs 9% 4y).
# category: money
# usage: compare loans <amt> <rate> <years> vs <rate> <years>
# rawargs: full
# patterns: \bcompare\b.*\bloans?\b ;; \bloans?\b.*\b(vs|versus)\b
# priority: 2
import re
from _lib import args_text, fail
t = args_text().lower().replace(",", "")
t = re.sub(r"^(?:please\s+)?(?:compare|loan comparison|loans?)\s*(?:loans?|offers?|emi)?\s*", "", t)
parts = re.split(r"\s+(?:vs\.?|versus|and|or|against)\s+", t, maxsplit=1)
if len(parts) != 2:
    fail("Usage: compare loans 500000 8.5% 5y vs 9% 4y   (amount, rate and years for the first; rate and years, or all three, for the second)")
def parse(s):
    mo = re.search(r"(\d+(?:\.\d+)?)\s*(?:months?|mo|m)\b", s)
    yr = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?|y)\b", s)
    s2 = re.sub(r"(\d+(?:\.\d+)?)\s*(?:months?|mo|m|years?|yrs?|y)\b", " ", s)
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", s2)]
    months = None
    if yr: months = float(yr.group(1)) * 12
    elif mo: months = float(mo.group(1))
    return nums, months
n1, m1 = parse(parts[0]); n2, m2 = parse(parts[1])
if len(n1) < 2 or not m1:
    fail("The first loan needs an amount, a rate and a time, e.g. 500000 8.5% 5y")
P = n1[0]; r1 = n1[1]
if len(n2) >= 2: P2, r2 = n2[0], n2[1]
elif len(n2) == 1: P2, r2 = P, n2[0]
else: fail("The second loan needs a rate, e.g. 9% 4y")
m2 = m2 or m1
def emi(P, rate, months):
    months = round(months); r = rate / 1200
    e = P / months if r == 0 else P * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return e, e * months - P, e * months, months
for P_, r_, m_ in ((P, r1, m1), (P2, r2, m2)):
    if not (P_ > 0 and 0 <= r_ <= 100 and 1 <= m_ <= 600):
        fail("Check the values: rate 0-100%, time 1-600 months, amount above 0.")
a, b = emi(P, r1, m1), emi(P2, r2, m2)
print(f"{'':16}{'Loan A':>16}{'Loan B':>16}")
print(f"{'Amount':16}{P:>16,.2f}{P2:>16,.2f}")
print(f"{'Rate':16}{str(r1) + '%':>16}{str(r2) + '%':>16}")
print(f"{'Months':16}{a[3]:>16}{b[3]:>16}")
print(f"{'Monthly payment':16}{a[0]:>16,.2f}{b[0]:>16,.2f}")
print(f"{'Total interest':16}{a[1]:>16,.2f}{b[1]:>16,.2f}")
print(f"{'Total paid':16}{a[2]:>16,.2f}{b[2]:>16,.2f}")
d = a[2] - b[2]
print("Loan B costs less overall by " + f"{d:,.2f}." if d > 0 else ("Loan A costs less overall by " + f"{-d:,.2f}." if d < 0 else "Both cost the same overall."))
if a[0] != b[0]:
    print(f"Loan {'A' if a[0] < b[0] else 'B'} has the lower monthly payment (by {abs(a[0] - b[0]):,.2f}).")
