# keywords: trip budget, travel budget, trip cost estimate, holiday budget, vacation budget
# desc: Estimate a trip budget (trip budget 4 days 2 people 3000 a day)
# category: travel
# usage: trip budget <days> days <n> people <amount> a day [fare <amount>]
# rawargs: yes
# patterns: \b(trip|travel|holiday|vacation)\s+budget\b ;; \btrip\s+cost\b
# priority: 2
import re
from _lib import args_text, fail
from _money import inr
t = args_text().lower().replace(",", "")
def pick(pat):
    m = re.search(pat, t)
    return float(m.group(1)) if m else None
days = pick(r"(\d+(?:\.\d+)?)\s*(?:days?|nights?)")
people = pick(r"(\d+)\s*(?:people|persons?|pax|members?|friends)") or 1
perday = pick(r"(?:rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:a|per|/)\s*(?:day|head|person)")
fare = pick(r"(?:fare|travel|tickets?|transport)\s*(?:rs\.?|inr)?\s*(\d+(?:\.\d+)?)") or 0
if not days or not perday or days <= 0 or perday <= 0 or people <= 0 or people > 500:
    fail("Usage: trip budget 4 days 2 people 3000 a day [fare 6000]\n  (3000 a day is per person: stay, food, local travel)")
stay = days * people * perday
total = stay + fare
buffer = total * 0.10
print(f"Trip: {days:g} days, {people:g} people")
print(f"  On the ground ({inr(perday)} x {days:g} days x {people:g}) : {inr(stay)}")
if fare:
    print(f"  Fares / tickets                         : {inr(fare)}")
print(f"  10% buffer for surprises                : {inr(buffer)}")
print(f"  Plan to carry                           : {inr(total + buffer)}  ({inr((total + buffer) / people)} each)")
