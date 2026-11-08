# keywords: profit margin, margin, markup, gross margin, selling price for margin, price for margin, cost price margin, profit percentage
# desc: Profit margin and markup, or the price you need for a target margin (profit margin cost 60 price 100 | price for 30% margin cost 70).
# category: money
# usage: profit margin cost <c> price <p>
# rawargs: full
# patterns: \b(profit\s+)?margin\b.*\d ;; \bmarkup\b.*\d
# priority: 1
import re
from _lib import args_text, fail
from _money import numbers
t = args_text().lower().replace(",", "")
n = numbers(t)
cost = re.search(r"cost\D{0,12}?(\d+(?:\.\d+)?)", t)
price = re.search(r"(?:price|sell\w*)\D{0,12}?(\d+(?:\.\d+)?)", t)
tgt = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:margin|profit)|margin\s*(?:of|at|target)\s*(\d+(?:\.\d+)?)", t)
if tgt and cost:
    mg = float(tgt.group(1) or tgt.group(2))
    c = float(cost.group(1))
    if not 0 <= mg < 100 or c <= 0:
        fail("Margin must be between 0 and 99.9, cost above 0.")
    p = c / (1 - mg / 100)
    print(f"To earn a {mg:g}% margin on cost {c:,.2f}:")
    print(f"  Sell at      : {p:,.2f}")
    print(f"  Profit each  : {p - c:,.2f}")
    print(f"  Markup       : {100 * (p - c) / c:.1f}%")
    raise SystemExit(0)
if cost and price:
    c, p = float(cost.group(1)), float(price.group(1))
elif len(n) >= 2:
    c, p = n[0], n[1]
else:
    fail("Usage: profit margin cost 60 price 100   |   price for 30% margin cost 70")
if c <= 0 or p <= 0:
    fail("Cost and price must be above 0.")
prof = p - c
print(f"Cost {c:,.2f}, price {p:,.2f}")
print(f"  Profit : {prof:,.2f}")
print(f"  Margin : {100 * prof / p:.1f}%   (profit / price)")
print(f"  Markup : {100 * prof / c:.1f}%   (profit / cost)")
