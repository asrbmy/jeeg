# keywords: roman numerals, roman numeral, to roman, from roman, roman number, convert roman, what is xiv, roman digits
# desc: Convert between Roman numerals and numbers (roman numeral 2026, or roman numeral MCMXC)
# category: text
# usage: roman numeral <number|numeral>
# rawargs: yes
import re
from _lib import args_text, fail
t = re.sub(r"\b(roman|numerals?|number|numbers|to|from|convert|what|is|in|of|digits?)\b", " ", args_text(), flags=re.I).strip()
V = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
if re.fullmatch(r"\d+", t):
    n = int(t)
    if not 1 <= n <= 3999: fail("Roman numerals cover 1 to 3999.")
    out = ""
    for v, s in V:
        while n >= v: out += s; n -= v
    print(f"{t} = {out}")
elif re.fullmatch(r"[IVXLCDMivxlcdm]+", t):
    u = t.upper()
    if not re.fullmatch(r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})", u): fail(f"'{t}' is not a valid Roman numeral.")
    val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    tot = sum(val[c] if i + 1 == len(u) or val[c] >= val[u[i + 1]] else -val[c] for i, c in enumerate(u))
    print(f"{u} = {tot}")
else:
    fail("Usage: roman numeral 2026   or   roman numeral MCMXC")
