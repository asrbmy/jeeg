# keywords: compound interest, interest, fd, fixed deposit, savings growth, deposit, ci, maturity, rd calculator, compounding
# desc: Compound interest (compound interest 10000 7 3 years [monthly])
# category: money
# usage: compound interest <amount> <rate%> <years>
# rawargs: yes
from _lib import args_text, fail
from _money import inr, numbers, tenure_months
t = args_text().lower().replace("%", " ")
freq = 12 if "month" in t and "months" not in t.split() and "monthly" in t else 4 if "quarter" in t else 2 if "half" in t else 1
months, rest = tenure_months(t.replace("monthly", " ").replace("quarterly", " "))
n = numbers(rest)
if months is None and len(n) >= 3:
    months = n.pop() * 12
if len(n) < 2 or not months:
    fail("Usage: compound interest <principal> <rate %> <years> [monthly|quarterly]")
P, rate, yrs = n[0], n[1], months / 12
if not (P > 0 and 0 <= rate <= 100 and 0 < yrs <= 100):
    fail("Check the values: rate 0-100%, up to 100 years.")
A = P * (1 + rate / 100 / freq) ** (freq * yrs)
name = {12: "monthly", 4: "quarterly", 2: "half-yearly", 1: "yearly"}[freq]
print(f"{inr(P)} at {rate:g}% for {yrs:g} years, compounded {name}")
print(f"  Interest earned: {inr(A - P)}")
print(f"  Final amount   : {inr(A)}")
