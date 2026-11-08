# keywords: sip goal, savings goal, how much to save, monthly investment needed, how much sip
# desc: Monthly saving needed to reach a goal (sip goal 1 million in 15 years at 8%; how much to save for 50000 in 3 years)
# category: money
# usage: sip goal <amount> in <years> years [at <rate>%]
# rawargs: yes
# patterns: \bsip\s+goal\b ;; \bhow\s+much\s+(sip|to\s+(save|invest))\b ;; \b(savings|investment)\s+goal\b
# priority: 3
import re
from _lib import args_text, fail
t = args_text().lower().replace(",", "")
units = {"k": 1e3, "thousand": 1e3, "m": 1e6, "mn": 1e6, "million": 1e6, "lakh": 1e5, "lakhs": 1e5, "lac": 1e5, "crore": 1e7, "crores": 1e7, "cr": 1e7, "b": 1e9, "billion": 1e9}
m = re.search(r"(\d+(?:\.\d+)?)\s*(" + "|".join(sorted(units, key=len, reverse=True)) + r")?\b", re.sub(r"\b(sip|goal|how|much|to|save|for|reach|target)\b", " ", t))
y = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", t)
r = re.search(r"(?:at|rate|return|returns)\D{0,6}(\d+(?:\.\d+)?)\s*%?", t) or re.search(r"(\d+(?:\.\d+)?)\s*%", t)
if not m or not y:
    fail("Usage: sip goal 1 million in 15 years at 8%     (goal amount, years, expected yearly return; default 8%)")
goal = float(m.group(1)) * units.get(m.group(2) or "", 1)
years = float(y.group(1))
rate = float(r.group(1)) if r else 8.0
if not (goal > 0 and 0 < years <= 80 and 0 <= rate <= 60):
    fail("Check the numbers: years 1-80, return 0-60%.")
n = int(round(years * 12))
i = rate / 1200
pay = goal / n if i == 0 else goal * i / ((1 + i) ** n - 1)
put = pay * n
print(f"To reach {goal:,.0f} in {years:g} years at {rate:g}% a year:")
print(f"  Save every month : {pay:,.2f}")
print(f"  You put in       : {put:,.0f}")
print(f"  Growth earns     : {goal - put:,.0f}")
later = (goal / (n - 12) if i == 0 else goal * i / ((1 + i) ** (n - 12) - 1)) if n > 12 else goal
print(f"  If you wait 1 year, you would need {later:,.2f} a month.")
print("  Returns are not guaranteed; this assumes the same rate every year.")
