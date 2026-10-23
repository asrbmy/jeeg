# keywords: sip, mutual fund, systematic investment, investment growth, invest monthly, returns, wealth, retirement corpus, monthly investment
# desc: SIP growth (sip 5000 12 10 years: monthly amount, yearly return %, years)
# category: money
# usage: sip <monthly> <return%> <years>
# rawargs: yes
from _lib import args_text, fail
from _money import inr, numbers, tenure_months, words
t = args_text().lower().replace("%", " ")
months, rest = tenure_months(t)
n = numbers(rest)
if months is None and len(n) >= 3:
    months = n.pop() * 12
if len(n) < 2 or not months:
    fail("Usage: sip <monthly amount> <expected yearly return %> <years>   e.g. sip 5000 12 10 years")
P, rate, months = n[0], n[1], round(months)
if not (P > 0 and 0 <= rate <= 60 and 1 <= months <= 720):
    fail("Check the values: return 0-60% a year, 1-720 months, amount above 0.")
i = rate / 12 / 100
fv = P * months if i == 0 else P * (((1 + i) ** months - 1) / i) * (1 + i)   # payments at the start of each month
inv = P * months
print(f"SIP {inr(P)}/month for {months / 12:g} years at {rate:g}% a year")
print(f"  Invested     : {inr(inv)}" + (f" ({words(inv)})" if words(inv) else ""))
print(f"  Estimated gain: {inr(fv - inv)}")
print(f"  Final value  : {inr(fv)}" + (f" ({words(fv)})" if words(fv) else ""))
print("  (an estimate: real returns vary and are not guaranteed)")
