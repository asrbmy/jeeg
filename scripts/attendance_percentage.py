# keywords: attendance, attendance percentage, bunk, classes can i skip, minimum attendance, attendance calculator
# desc: Attendance percentage and classes you can skip (attendance 42 of 50; need 75)
# category: study
# usage: attendance <attended> of <total> [need <percent>]
# rawargs: yes
# patterns: \battendance\b ;; \b(bunk|skip)\s+(how\s+many\s+)?(classes|lectures)\b
# priority: 2
import math, re
from _lib import args_text, fail
from _money import numbers
t = args_text().lower()
need = 75.0
m = re.search(r"(?:need|required|minimum|min|target)\D{0,6}(\d+(?:\.\d+)?)", t)
if m:
    need = float(m.group(1))
    t = t[:m.start()] + " " + t[m.end():]
n = numbers(re.sub(r"\b(attendance|attended|of|out|classes|lectures|total|percentage|can|skip|bunk|i)\b", " ", t))
if len(n) < 2 or n[1] <= 0 or not 0 <= n[0] <= n[1] or not 0 < need < 100:
    fail("Usage: attendance 42 of 50   (add 'need 80' if your minimum is not 75)")
a, tot = int(n[0]), int(n[1])
p = a / tot * 100
print(f"Attendance: {a} of {tot} = {p:.1f}%  (minimum {need:g}%)")
if p >= need:
    skip = math.floor(a * 100 / need - tot)
    print(f"  You can miss {skip} more class{'es' if skip != 1 else ''} and stay at or above {need:g}%.")
else:
    k = math.ceil((need * tot - 100 * a) / (100 - need))
    print(f"  Attend the next {k} classes in a row to reach {need:g}%.")
