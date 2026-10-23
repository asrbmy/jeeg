# keywords: emi, loan, home loan, car loan, personal loan, monthly payment, installment, instalment, interest rate
# desc: Loan EMI (emi 5 lakh 8.5 5 years)
# category: money
# usage: emi <amount> <rate%> <years>
# rawargs: yes
from _lib import args_text, fail
from _money import inr, numbers, tenure_months, words
t = args_text().lower().replace("%", " ")
months, rest = tenure_months(t)
n = numbers(rest)
if months is None and len(n) >= 3:
    months = n.pop() * 12                       # third bare number = years
if len(n) < 2 or not months:
    fail("Usage: emi <amount> <annual rate %> <tenure>   e.g. emi 5 lakh 8.5 5 years   |   emi 2500000 9 20 years")
P, rate = n[0], n[1]
months = round(months)
if not (P > 0 and 0 <= rate <= 100 and 1 <= months <= 600):
    fail("Check the values: rate 0-100%, tenure 1-600 months, amount above 0.")
r = rate / 12 / 100
emi = P / months if r == 0 else P * r * (1 + r) ** months / ((1 + r) ** months - 1)
total = emi * months
print(f"Loan {inr(P)}" + (f" ({words(P)})" if words(P) else "") + f" at {rate:g}% for {months} months ({months / 12:g} years)")
print(f"  Monthly EMI    : {inr(emi)}")
print(f"  Total interest : {inr(total - P)}")
print(f"  Total payment  : {inr(total)}")
print(f"  First month    : interest {inr(P * r)}, principal {inr(emi - P * r)}")
