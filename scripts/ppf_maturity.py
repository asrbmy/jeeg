# keywords: ppf, public provident fund, ppf maturity, ppf calculator, ppf interest
# desc: PPF maturity (ppf 1.5 lakh a year; ppf 50000 a year 15 years)
# category: money
# usage: ppf <amount a year> [years] [rate %]
# rawargs: yes
# patterns: \bppf\b ;; \bpublic\s+provident\s+fund\b
# priority: 2
import re
from _lib import args_text, fail
from _money import inr
t = args_text().lower().replace(",", "")
m = re.search(r"(\d+(?:\.\d+)?)\s*(lakhs?|lacs?|l|k)?", re.sub(r"\bppf\b", " ", t))
if not m:
    fail("Usage: ppf 1.5 lakh a year   (add '15 years' and 'rate 7.1' if you like)")
a = float(m.group(1)) * {"lakh": 1e5, "lakhs": 1e5, "lac": 1e5, "lacs": 1e5, "l": 1e5, "k": 1e3}.get(m.group(2) or "", 1)
y = re.search(r"(\d+)\s*(?:years?|yrs?)", t)
r = re.search(r"(?:rate\s*)?(\d+(?:\.\d+)?)\s*%", t) or re.search(r"rate\s*(\d+(?:\.\d+)?)", t)
years = int(y.group(1)) if y else 15
rate = float(r.group(1)) if r else 7.1
if not (0 < a <= 150000) or not (15 <= years <= 50) or not (0 <= rate <= 20):
    fail("PPF allows 500 to 1,50,000 a year, for 15 years or more (extensions come in 5 year blocks).")
bal = 0.0
for _ in range(years):
    bal = (bal + a) * (1 + rate / 100)                # deposits early in the year, interest yearly
put = a * years
print(f"PPF {inr(a)} a year for {years} years at {rate:g}% (interest is tax free)")
print(f"  You deposit : {inr(put)}")
print(f"  Interest    : {inr(bal - put)}")
print(f"  Maturity    : {inr(bal)}")
print("  (Deposit by the 5th of April-month for a full year of interest. The rate is revised every quarter.)")
