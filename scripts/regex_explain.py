# keywords: regex explain, explain regex, regular expression explained, what does this regex do
# desc: Explain a regular expression in plain words (regex explain ^\d{3}-\w+$)
# category: developer
# usage: regex explain <pattern>
# rawargs: full
# patterns: \bregex\s+(explain|meaning|explained)\b ;; \bwhat\s+does\s+(this\s+)?regex\b ;; \b(explain|decode)\s+(this\s+|the\s+)?regular\s+expression\b
# priority: 4
import re
from _lib import args_text, fail
t = args_text().strip()
t = re.sub(r"^(?:please\s+)?(?:(?:explain|what\s+does|decode|read)\s+(?:this\s+|the\s+)?)?(?:regex|regular\s+expression|pattern)\s*(?:explain|explained|meaning|mean|do)?\s*[:\-]?\s*", "", t, flags=re.I).strip()
if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'/":
    t = t[1:-1]
if not t or len(t) > 300:
    fail("Usage: explain regex ^\\d{3}-\\w+$      (up to 300 characters)")
try:
    re.compile(t)
except re.error as e:
    fail(f"That is not a valid regular expression: {e}")
cls = {"d": "a digit", "D": "a non-digit", "w": "a letter, digit or _", "W": "a symbol or space", "s": "a space or tab", "S": "anything but whitespace",
       "b": "a word boundary", "B": "not a word boundary", "n": "a new line", "t": "a tab", "A": "the very start", "Z": "the very end"}
out, i = [], 0
def quant(j):
    if j < len(t) and t[j] in "*+?":
        lazy = j + 1 < len(t) and t[j + 1] == "?"
        txt = {"*": "zero or more times", "+": "one or more times", "?": "optional"}[t[j]] + (" (as few as possible)" if lazy else "")
        return txt, j + 1 + (1 if lazy else 0)
    m = re.match(r"\{(\d+)(,(\d*))?\}", t[j:])
    if m:
        a, comma, b = m.group(1), m.group(2), m.group(3)
        txt = f"exactly {a} times" if not comma else (f"{a} or more times" if b == "" else f"{a} to {b} times")
        return txt, j + m.end()
    return "", j
while i < len(t):
    c = t[i]
    if c == "\\" and i + 1 < len(t):
        n = t[i + 1]
        what = cls.get(n, f"the character '{n}'" if not n.isalnum() else f"the escape \\{n}")
        i += 2
    elif c == "[":
        j = t.find("]", i + 2 if i + 1 < len(t) and t[i + 1] == "^" else i + 1)
        j = len(t) - 1 if j < 0 else j
        body = t[i + 1:j]
        neg = body.startswith("^")
        what = ("any character except " if neg else "one of ") + "[" + body.lstrip("^") + "]"
        i = j + 1
    elif c == "(":
        if t.startswith("(?:", i): what, i = "start of a non-capturing group", i + 3
        elif t.startswith("(?=", i): what, i = "start of a look-ahead (must be followed by)", i + 3
        elif t.startswith("(?!", i): what, i = "start of a negative look-ahead (must NOT be followed by)", i + 3
        elif t.startswith("(?<=", i): what, i = "start of a look-behind (must be preceded by)", i + 4
        elif t.startswith("(?P<", i) or t.startswith("(?<", i):
            k = t.find(">", i)
            what, i = f"start of a group named '{t[t.find('<', i) + 1:k]}'", k + 1
        else: what, i = "start of a group (captured)", i + 1
    elif c == ")": what, i = "end of group", i + 1
    elif c == "|": what, i = "OR", i + 1
    elif c == "^": what, i = "the start of the text", i + 1
    elif c == "$": what, i = "the end of the text", i + 1
    elif c == ".": what, i = "any character", i + 1
    else: what, i = f"the character '{c}'", i + 1
    q, i2 = quant(i) if what != "OR" and not what.startswith("start of") else ("", i)
    out.append(what + (f", {q}" if q else ""))
    i = i2
print(f"Regex: {t}")
for n, line in enumerate(out, 1):
    print(f"  {n:>2}. {line}")
print("Test it with:  regex tester")
