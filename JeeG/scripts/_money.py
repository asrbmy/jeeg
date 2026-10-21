"""Money parsing, Indian digit grouping and live currency rates. Not a task."""
import re

from _lib import fail
from _net import get

MULT = {"k": 1e3, "thousand": 1e3, "lakh": 1e5, "lakhs": 1e5, "lac": 1e5, "lacs": 1e5, "cr": 1e7,
        "crore": 1e7, "crores": 1e7, "m": 1e6, "mn": 1e6, "million": 1e6, "b": 1e9, "bn": 1e9, "billion": 1e9}
_NUM = re.compile(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s*(" + "|".join(sorted(MULT, key=len, reverse=True)) + r")?(?![a-z])", re.I)


def numbers(text):
    """All numbers in text with k / lakh / crore / m suffixes applied: '5 lakh 8.5%' -> [500000.0, 8.5]."""
    out = []
    for m in _NUM.finditer(text):
        v = float(m.group(1).replace(",", ""))
        out.append(v * MULT[m.group(2).lower()] if m.group(2) else v)
    return out


def tenure_months(text):
    """Find '5 years' / '18 months' -> (months, text_without_it) or (None, text)."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*(years?|yrs?|y|months?|mos?|m)\b", text, re.I)
    if not m:
        return None, text
    n = float(m.group(1))
    months = n * 12 if m.group(2).lower().startswith("y") else n
    return months, text[:m.start()] + " " + text[m.end():]


def inr(x, decimals=2):
    """Indian digit grouping: 1234567.5 -> 12,34,567.50"""
    neg = x < 0
    s = f"{abs(x):.{decimals}f}"
    whole, _, frac = s.partition(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        if head:
            parts.insert(0, head)
        whole = ",".join(parts) + "," + tail
    return ("-" if neg else "") + whole + (("." + frac) if decimals else "")


def words(x):
    """500000 -> '5.00 lakh', 25000000 -> '2.50 crore' (for readability)."""
    a = abs(x)
    if a >= 1e7: return f"{x / 1e7:.2f} crore"
    if a >= 1e5: return f"{x / 1e5:.2f} lakh"
    return ""


NAMES = {"dollar": "USD", "dollars": "USD", "usd": "USD", "euro": "EUR", "euros": "EUR", "eur": "EUR",
         "rupee": "INR", "rupees": "INR", "inr": "INR", "rs": "INR", "pound": "GBP", "pounds": "GBP", "gbp": "GBP",
         "yen": "JPY", "jpy": "JPY", "dirham": "AED", "dirhams": "AED", "aed": "AED", "yuan": "CNY", "cny": "CNY",
         "riyal": "SAR", "sar": "SAR", "franc": "CHF", "chf": "CHF", "won": "KRW", "krw": "KRW", "baht": "THB",
         "thb": "THB", "ringgit": "MYR", "myr": "MYR", "aud": "AUD", "cad": "CAD", "sgd": "SGD", "nzd": "NZD",
         "hkd": "HKD", "pkr": "PKR", "bdt": "BDT", "lkr": "LKR", "npr": "NPR", "rub": "RUB", "brl": "BRL",
         "zar": "ZAR", "try": "TRY", "sek": "SEK", "nok": "NOK", "dkk": "DKK", "mxn": "MXN", "idr": "IDR"}


def code(word):
    w = word.strip().lower()
    if w in NAMES:
        return NAMES[w]
    return w.upper() if re.fullmatch(r"[a-z]{3}", w) else None


def currency_cli(text):
    """'100 usd to inr' -> prints a live conversion. Returns False if the text is not a currency request."""
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*([a-z]+)\s+(?:to|in|into|as)\s+([a-z]+)", text.lower())
    if not m:
        return False
    a, b = code(m.group(2)), code(m.group(3))
    if not a or not b:
        return False
    amt = float(m.group(1).replace(",", ""))
    data = get(f"https://open.er-api.com/v6/latest/{a}", timeout=8, as_json=True)
    if not data:
        fail("Could not fetch live exchange rates (offline?).")
    if data.get("result") != "success" or b not in data.get("rates", {}):
        fail(f"Unknown currency code ({a} or {b}).")
    rate = data["rates"][b]
    res = amt * rate
    fmt = inr if b == "INR" else (lambda v: f"{v:,.2f}")
    print(f"{amt:,.2f} {a} = {fmt(res)} {b}")
    print(f"(1 {a} = {rate:.4f} {b}; rates updated {data.get('time_last_update_utc', '?')[:16]})")
    return True
