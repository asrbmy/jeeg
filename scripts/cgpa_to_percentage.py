# keywords: cgpa, cgpa to percentage, cgpa percentage, convert cgpa, sgpa to percentage
# desc: Convert CGPA to percentage (cgpa 8.2 to percentage; cbse 9.4)
# category: study
# usage: cgpa <value> [out of 4]
# rawargs: yes
# patterns: \bcgpa\b ;; \bsgpa\s+to\s+percent
# priority: 2
import re
from _lib import args_text, fail
t = args_text().lower()
m = re.search(r"(\d+(?:\.\d+)?)", t)
if not m:
    fail("Usage: cgpa 8.2   (add 'out of 8' or 'out of 4' for other scales)")
g = float(m.group(1))
s = re.search(r"\b(?:out of|/|scale)\s*(\d+(?:\.\d+)?)", t)
scale = float(s.group(1)) if s else 10.0
if not (0 <= g <= scale):
    fail(f"CGPA must be between 0 and {scale:g}.")
if scale == 10:
    print(f"CGPA {g:g}/10 is about {g * 9.5:.1f}% (CBSE formula: CGPA x 9.5)")
    print(f"  Many universities use CGPA x 10 = {g * 10:.1f}% - check your own university's rule.")
else:
    print(f"CGPA {g:g}/{scale:g} is about {g / scale * 100:.1f}% (simple proportion; your university may differ).")
