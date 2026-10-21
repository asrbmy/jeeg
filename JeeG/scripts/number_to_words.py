# keywords: number to words, write number in words, spell number, number in words, cheque amount in words, amount in words, say number, rupees in words, digits to words
# desc: Write a number in words, Indian and international style (number to words 1234567)
# category: text
# usage: number to words <number>
# rawargs: yes
import re
from decimal import Decimal, InvalidOperation
from _lib import args_text, fail
from _text import words_intl, words_indian, indian_group, ONES
t = re.sub(r"\b(rs|inr|rupees?|number|amount|to|words?|in|of|the|write|spell|say|digits?|as)\b|[₹$,]", " ", args_text(), flags=re.I).strip()
MULT = {"crore": 10**7, "cr": 10**7, "lakh": 10**5, "lac": 10**5, "lakhs": 10**5, "crores": 10**7, "thousand": 1000, "k": 1000, "million": 10**6, "mn": 10**6, "billion": 10**9, "bn": 10**9, "trillion": 10**12}
mm = re.fullmatch(r"(-?[\d.]+)\s*([a-z]+)", t, re.I)
mult = 1
if mm and mm.group(2).lower() in MULT: t, mult = mm.group(1), MULT[mm.group(2).lower()]
t = t.replace(" ", "")
try:
    d = Decimal(t) * mult
except InvalidOperation:
    fail("Usage: number to words 1234567   (decimals and negatives work too)")
if not d.is_finite() or abs(d) >= 10 ** 18: fail("That number is too large (limit: below one quintillion).")
neg = d < 0; d = abs(d)
whole, _, frac = format(d, "f").partition(".")
n = int(whole); frac = frac.rstrip("0")
dec = (" point " + " ".join(ONES[int(c)] for c in frac)) if frac else ""
sign = "minus " if neg else ""
print(f"{'-' if neg else ''}{indian_group(whole)}{('.' + frac) if frac else ''}  (Indian grouping)")
print(f"Indian:        {sign}{words_indian(n)}{dec}")
print(f"International: {sign}{words_intl(n)}{dec}")
