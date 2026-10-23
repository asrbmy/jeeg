# keywords: rd, recurring deposit, rd maturity, monthly deposit, post office rd
# desc: Recurring deposit maturity (rd 5000 a month 6.5% 2 years)
# category: money
# usage: rd <monthly amount> <rate %> <years>
# rawargs: yes
# patterns: ^\s*rd\b ;; \brecurring\s+deposit\b ;; \brd\s+(calculator|maturity)\b
# priority: 2
import re
from _lib import args_text, fail
from _money import inr, numbers, tenure_months
t = args_text().lower().replace("%", " ")
months, rest = tenure_months(t)
rest = re.sub(r"\b(rd|recurring|deposit|monthly|month|a|per|every|each)\b", " ", rest)
n = numbers(rest)
if months is None and len(n) >= 3:
    months = n.pop() * 12
if len(n) < 2 or not months:
    fail("Usage: rd <monthly amount> <rate %> <years>   e.g. rd 5000 6.5 2 years")
d, rate, m = n[0], n[1], int(round(months))
if not (d > 0 and 0 <= rate <= 100 and 1 <= m <= 1200):
    fail("Check the values: rate 0-100%, 1 to 1200 months.")
q = rate / 400                                   # Indian banks compound RD quarterly
total = 0.0
for k in range(m):                               # deposit k earns for (m - k) months
    total += d * (1 + q) ** ((m - k) / 3)
put = d * m
print(f"RD of {inr(d)} a month at {rate:g}% for {m} months (compounded quarterly)")
print(f"  You deposit : {inr(put)}")
print(f"  Interest    : {inr(total - put)}")
print(f"  Maturity    : {inr(total)}")
print("  (Banks differ by a few rupees because of rounding and day counts.)")
