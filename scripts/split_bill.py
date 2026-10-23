# keywords: split bill, split, bill, share, divide bill, per person, restaurant bill, tip, dutch, split the cost, each person pays
# desc: Split a bill (split bill 2400 among 4 tip 10%)
# category: money
# usage: split bill <amount> among <n> [tip %]
# rawargs: yes
import re
from _lib import args_text, fail
from _money import inr, numbers
t = args_text().lower()
tip = 0.0
m = re.search(r"tip\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%?|(\d+(?:\.\d+)?)\s*%\s*tip", t)
if m:
    tip = float(m.group(1) or m.group(2)); t = t[:m.start()] + " " + t[m.end():]
p = re.search(r"(?:among|between|by|for|with)\s+(\d+)|(\d+)\s*(?:people|persons|friends|ways)", t)
people = int(p.group(1) or p.group(2)) if p else None
if p: t = t[:p.start()] + " " + t[p.end():]
n = numbers(t)
if not n or not people or people < 1 or people > 1000:
    fail("Usage: split bill <amount> among <people> [tip 10%]   e.g. split bill 2400 among 4 tip 10%")
bill = n[0]
total = bill * (1 + tip / 100)
print(f"Bill {inr(bill)}" + (f" + {tip:g}% tip = {inr(total)}" if tip else "") + f", split {people} ways")
print(f"  Each person pays: {inr(total / people)}")
