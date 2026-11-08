# keywords: scale recipe, recipe scale, change servings, double recipe, halve recipe, recipe for more people
# desc: Scale ingredient amounts for a new number of servings (recipe scale 4 to 6: 2 cups flour, 1.5 tsp salt, 3 eggs)
# category: personal
# usage: recipe scale <from> to <to>: <ingredients separated by commas>
# rawargs: yes
import re
import sys
from fractions import Fraction

t = " ".join(sys.argv[1:])
m = re.search(r"(\d+(?:\.\d+)?)\s*(?:to|->|for)\s*(\d+(?:\.\d+)?)\s*(?:servings?|people)?\s*[:\-]\s*(.+)$", t, re.I | re.S)
if not m:
    sys.exit("Usage: recipe scale 4 to 6: 2 cups flour, 1.5 tsp salt, 3 eggs")
a, b, items = float(m.group(1)), float(m.group(2)), m.group(3)
if a <= 0 or b <= 0 or b / a > 100:
    sys.exit("Servings must be positive, and at most 100 times the original.")
k = b / a
UNI = {"½": "1/2", "¼": "1/4", "¾": "3/4", "⅓": "1/3", "⅔": "2/3"}
def num(s):
    for u, r in UNI.items():
        s = s.replace(u, " " + r)
    parts = s.split()
    return sum(Fraction(p) for p in parts)
def nice(x):
    f = Fraction(x).limit_denominator(8)
    whole, frac = divmod(f.numerator, f.denominator)
    if f.denominator == 1:
        return str(whole)
    return (f"{whole} " if whole else "") + f"{frac}/{f.denominator}"
print(f"Scaled from {a:g} to {b:g} servings (x{k:.3g}):")
for it in [x.strip() for x in re.split(r"[,;\n]", items) if x.strip()][:60]:
    mm = re.match(r"^((?:\d+\s+)?\d+/\d+|\d+(?:\.\d+)?|[½¼¾⅓⅔])\s*(.*)$", it)
    if not mm:
        print(f"  {it}   (no amount, left as it is)")
        continue
    try:
        v = num(mm.group(1)) * Fraction(k).limit_denominator(1000)
    except (ValueError, ZeroDivisionError):
        print(f"  {it}   (could not read the amount)")
        continue
    print(f"  {nice(v)} {mm.group(2)}")
