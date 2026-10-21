"""Helpers for text tasks. Not a task itself."""
import re
import sys

from _lib import args_text, fail

ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
        "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
INTL = ["", "thousand", "million", "billion", "trillion", "quadrillion"]


def three(n):
    """0 < n < 1000 -> words."""
    out = []
    if n >= 100:
        out.append(ONES[n // 100] + " hundred")
        n %= 100
    if n >= 20:
        out.append(TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else ""))
    elif n:
        out.append(ONES[n])
    return " ".join(out)


def words_intl(n):
    if n == 0:
        return "zero"
    parts, i = [], 0
    while n:
        n, r = divmod(n, 1000)
        if r:
            parts.append(three(r) + (" " + INTL[i] if INTL[i] else ""))
        i += 1
    return " ".join(reversed(parts))


def words_indian(n):
    if n == 0:
        return "zero"
    if n < 1000:
        return three(n)
    crore, rem = divmod(n, 10_000_000)
    lakh, rem = divmod(rem, 100_000)
    thou, rem = divmod(rem, 1000)
    parts = []
    if crore:
        parts.append(words_indian(crore) + " crore")
    if lakh:
        parts.append(three(lakh) + " lakh")
    if thou:
        parts.append(three(thou) + " thousand")
    if rem:
        parts.append(three(rem))
    return " ".join(parts)


def indian_group(s):
    """'1234567' -> '12,34,567'"""
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    head = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head)
    return head + "," + tail


def get_text(strip_words=""):
    """Text from the command (leading verbs like 'make'/'convert' and a trailing 'to'/'in' are dropped), else the clipboard."""
    t = args_text()
    lead = "make|convert|change|turn|put|write|type" + ("|" + strip_words if strip_words else "")
    t = re.sub(r"^\s*(?:(?:%s)\b\s*)+" % lead, "", t, flags=re.I)
    t = re.sub(r"\s+(?:to|in|into|as)\s*$", "", t, flags=re.I)
    if t.strip():
        return t
    from _sys import clip_get
    try:
        t = clip_get()
    except SystemExit:
        t = ""
    if not t.strip():
        fail("Give me some text after the task name, or copy text first.")
    return t


def emit(result):
    """Print the result and quietly put it on the clipboard when one is available."""
    import contextlib
    import io
    print(result)
    try:
        from _sys import clip_set
        with contextlib.redirect_stdout(io.StringIO()):
            clip_set(result)
        print("(copied to clipboard)")
    except (SystemExit, Exception):
        pass


def items(text):
    """Split into list items: lines if there are several, otherwise comma/semicolon separated."""
    if "\n" in text.strip():
        return [x.strip() for x in text.splitlines() if x.strip()]
    return [x.strip() for x in re.split(r"[;,]", text) if x.strip()]
