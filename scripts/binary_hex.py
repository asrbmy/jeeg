# keywords: binary, hex, hexadecimal, octal, decimal to binary, binary to decimal, hex to decimal, convert base, number base, bits
# desc: Convert a number between decimal, binary, hex and octal (binary 1010, hex ff, 255)
# category: text
# usage: binary|hex|octal <number>
# rawargs: full
# patterns: \b(binary|hexadecimal|hex|octal)\b ;; \b0x[0-9a-f]+\b ;; \b0b[01]+\b
import re
from _lib import args_text, fail
t = re.sub(r"\b(convert|to|from|in|of|number|decimal|dec|what|is|the|value|base)\b", " ", args_text(), flags=re.I)
m = re.search(r"\b(binary|bin|hexadecimal|hex|octal|oct)\b", t, re.I)
kind = m.group(1).lower() if m else ""
if re.search(r"\b(?:in|to|into|as)\s+(?:binary|bin|hexadecimal|hex|octal|oct)\b", args_text(), re.I): kind = ""   # "255 in binary": input is decimal
v = re.sub(r"\b(binary|bin|hexadecimal|hex|octal|oct)\b", " ", t, flags=re.I).strip().replace("_", "").replace(" ", "")
try:
    if v.lower().startswith("0x"): n = int(v, 16)
    elif v.lower().startswith("0b"): n = int(v, 2)
    elif v.lower().startswith("0o"): n = int(v, 8)
    elif kind.startswith("b"): n = int(v, 2)
    elif kind.startswith("h"): n = int(v, 16)
    elif kind.startswith("o"): n = int(v, 8)
    else: n = int(v)
except ValueError:
    fail("Usage: binary 1010 | hex ff | octal 17 | 255 | 0xff")
if n < 0 or n >= 2 ** 128: fail("Use a whole number from 0 up to 2^128.")
print(f"decimal: {n:,}\nbinary:  {n:b}\nhex:     {n:X}\noctal:   {n:o}")
