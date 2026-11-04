# keywords: marks percentage, percentage of marks, marks to percentage, exam percentage, score percentage
# desc: Percentage from marks (marks 432 out of 500)
# category: study
# usage: marks <obtained> out of <total>
# rawargs: yes
# patterns: \bmarks?\s+\d ;; \bpercentage\s+of\s+marks\b ;; \bexam\s+percentage\b
# priority: 2
import re
from _lib import args_text, fail
from _money import numbers
t = re.sub(r"\b(marks?|percentage|percent|out|of|obtained|scored|got|total|my|exam|score)\b", " ", args_text().lower())
n = numbers(t)
if len(n) < 2 or n[1] <= 0 or n[0] < 0 or n[0] > n[1]:
    fail("Usage: marks 432 out of 500")
p = n[0] / n[1] * 100
grade = "Distinction" if p >= 75 else "First class" if p >= 60 else "Second class" if p >= 50 else "Pass" if p >= 35 else "Below pass mark"
print(f"{n[0]:g} out of {n[1]:g} = {p:.2f}%  ({grade})")
