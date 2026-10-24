# keywords: loan prepay, loan prepayment, prepay loan, extra emi, pay loan early, interest saved
# desc: How much interest and time an extra monthly payment saves (loan prepay 5 lakh 8.5 5 years extra 2000)
# category: money
# usage: loan prepay <amount> <rate %> <years> extra <per month>
# rawargs: yes
import re
import sys

MULT = {"k": 1e3, "thousand": 1e3, "lakh": 1e5, "lakhs": 1e5, "lac": 1e5, "cr": 1e7, "crore": 1e7, "crores": 1e7}


def num(s):
    m = re.fullmatch(r"([\d,]+(?:\.\d+)?)\s*([a-z]*)", s.strip().lower())
    if not m:
        return None
    return float(m.group(1).replace(",", "")) * MULT.get(m.group(2), 1)


def inr(x):
    s, neg = f"{abs(x):.0f}", x < 0
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        s = ",".join(([head] if head else []) + parts + [tail])
    return ("-" if neg else "") + s


def run(principal, rate, months, extra):
    r, bal, paid, n = rate / 1200, principal, 0.0, 0
    emi = principal / months if r == 0 else principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    while bal > 0.005 and n < 1200:
        interest = bal * r
        pay = min(bal + interest, emi + extra)
        bal = bal + interest - pay
        paid += pay
        n += 1
    return emi, paid, n


t = " ".join(sys.argv[1:]).lower().replace("%", " ")
t = re.sub(r"\b(loan|prepay|prepayment|extra|emi|rs|inr|pay|per|a|month|monthly|early)\b", " ", t)
ym = re.search(r"(\d+(?:\.\d+)?)\s*(years?|yrs?|y|months?|mos?)\b", t)
if not ym:
    sys.exit("Usage: loan prepay <amount> <rate %> <years> extra <per month>   e.g. loan prepay 5 lakh 8.5 5 years extra 2000")
months = round(float(ym.group(1)) * (12 if ym.group(2).startswith("y") else 1))
t = t[:ym.start()] + " " + t[ym.end():]
toks = re.findall(r"[\d,]+(?:\.\d+)?\s*(?:lakhs?|lacs?|crores?|cr|k|thousand)?", t)
vals = [v for v in (num(x) for x in toks) if v is not None]
if len(vals) < 3 or not 1 <= months <= 600:
    sys.exit("I need the loan amount, the rate, the time and the extra amount. Example: loan prepay 5 lakh 8.5 5 years extra 2000")
principal, rate, extra = vals[0], vals[1], vals[2]
if not (principal > 0 and 0 <= rate <= 60 and 0 <= extra <= principal):
    sys.exit("Please check the numbers.")
emi, base_paid, base_n = run(principal, rate, months, 0)
_, new_paid, new_n = run(principal, rate, months, extra)
print(f"Loan {inr(principal)} at {rate:g}% for {months} months: EMI {inr(emi)}")
print(f"  Without extra : total interest {inr(base_paid - principal)}, done in {base_n} months")
print(f"  With +{inr(extra)}/mo: total interest {inr(new_paid - principal)}, done in {new_n} months")
print(f"  You save {inr(base_paid - new_paid)} of interest and finish {base_n - new_n} month(s) earlier.")
print("  (Check with your bank for prepayment charges.)")
