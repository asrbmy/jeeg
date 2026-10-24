# keywords: goal planner, savings goal, goal sip, how much to save monthly, plan goal, target amount
# desc: Monthly saving needed to reach a goal (goal planner 10 lakh in 5 years at 12%)
# category: money
# usage: goal planner <target> in <years> at <rate %>
# rawargs: yes
import re
import sys

MULT = {"k": 1e3, "thousand": 1e3, "lakh": 1e5, "lakhs": 1e5, "lac": 1e5, "cr": 1e7, "crore": 1e7, "crores": 1e7}
t = " ".join(sys.argv[1:]).lower().replace("%", " ")
ym = re.search(r"(\d+(?:\.\d+)?)\s*(years?|yrs?|y|months?|mos?)\b", t)
if not ym:
    sys.exit("Usage: goal planner <target> in <years> at <rate %>   e.g. goal planner 10 lakh in 5 years at 12%")
months = round(float(ym.group(1)) * (12 if ym.group(2).startswith("y") else 1))
t = t[:ym.start()] + " " + t[ym.end():]
vals = []
for m in re.finditer(r"([\d,]+(?:\.\d+)?)\s*(lakhs?|lacs?|crores?|cr|k|thousand)?\b", t):
    vals.append(float(m.group(1).replace(",", "")) * MULT.get(m.group(2) or "", 1))
if len(vals) < 2 or not 1 <= months <= 720:
    sys.exit("I need a target amount and a yearly return rate.")
target, rate = vals[0], vals[1]
if not (target > 0 and 0 <= rate <= 50):
    sys.exit("Please check the numbers.")


def inr(x):
    s = f"{x:.0f}"
    if len(s) > 3:
        head, tail, parts = s[:-3], s[-3:], []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        s = ",".join(([head] if head else []) + parts + [tail])
    return s


r = rate / 1200
need = target / months if r == 0 else target * r / (((1 + r) ** months - 1) * (1 + r))
print(f"To reach {inr(target)} in {months} months at {rate:g}% a year:")
print(f"  Save about {inr(need)} a month (you put in {inr(need * months)})")
print(f"  Growth does the rest: about {inr(target - need * months)}")
print("  Returns are not guaranteed; this assumes a steady rate and a deposit at the start of each month.")
