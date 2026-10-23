# keywords: percentage change, percent change, increase, decrease, growth, how much percent, percent increase, percent decrease, change percent, difference percent, hike
# desc: Percentage change between two numbers (percentage change 80 to 100)
# category: money
# usage: percentage change <old> to <new>
# rawargs: yes
from _lib import args_text, fail
from _money import numbers
n = numbers(args_text().lower().replace("%", " "))
if len(n) < 2:
    fail("Usage: percentage change <old> to <new>   e.g. percentage change 80 to 100")
a, b = n[0], n[1]
if a == 0:
    fail("The starting value cannot be zero.")
ch = (b - a) / abs(a) * 100
print(f"{a:g} -> {b:g}: {'+' if ch >= 0 else ''}{ch:.2f}%  ({'increase' if ch > 0 else 'decrease' if ch < 0 else 'no change'} of {abs(b - a):g})")
