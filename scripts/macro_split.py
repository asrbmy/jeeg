# keywords: macros, macro split, protein carbs fat, daily macros, macro calculator, nutrient split
# desc: Split daily calories into protein, carbs and fat (macros 2000 calories)
# category: health
# usage: macros <calories> [high protein | low carb]
# rawargs: yes
# patterns: \bmacros?\b ;; \bprotein\s+carbs?\s+(and\s+)?fat\b
# priority: 2
import re
from _lib import args_text, fail
from _money import numbers
t = args_text().lower()
n = numbers(t)
if not n or not (800 <= n[0] <= 8000):
    fail("Usage: macros 2000 calories   (add 'high protein' or 'low carb')")
c = n[0]
p, cb, f = (.30, .40, .30) if "high protein" in t else (.30, .25, .45) if "low carb" in t else (.20, .50, .30)
print(f"{c:g} kcal a day" + (" (high protein)" if p == .30 and cb == .40 else " (low carb)" if cb == .25 else " (balanced)"))
print(f"  Protein : {c * p / 4:>5.0f} g  ({p * 100:.0f}%)")
print(f"  Carbs   : {c * cb / 4:>5.0f} g  ({cb * 100:.0f}%)")
print(f"  Fat     : {c * f / 9:>5.0f} g  ({f * 100:.0f}%)")
