# keywords: electricity bill, power bill, light bill, units to bill, bijli bill, current bill estimate
# desc: Estimate an electricity bill (electricity bill 250 units at 7)
# category: home
# usage: electricity bill <units> at <rate> [fixed <amt>]
# rawargs: yes
# patterns: \b(electricity|power|light|bijli)\s+bill\b ;; \bunits\s+(to|into)\s+bill\b
# priority: 2
import re
from _lib import args_text, fail
from _money import inr
t = args_text().lower()
u = re.search(r"(\d+(?:\.\d+)?)\s*units?", t) or re.search(r"(\d+(?:\.\d+)?)", t)
r = re.search(r"(?:at|rate|@)\s*(?:rs\.?)?\s*(\d+(?:\.\d+)?)", t)
fx = re.search(r"fixed\s*(\d+(?:\.\d+)?)", t)
if not u or not r:
    fail("Usage: electricity bill 250 units at 7   (rate per unit; add 'fixed 120' for a fixed charge)")
units, rate, fixed = float(u.group(1)), float(r.group(1)), float(fx.group(1)) if fx else 0.0
energy = units * rate
duty = energy * 0.05
print(f"{units:g} units x {inr(rate)} = {inr(energy)}")
if fixed:
    print(f"  Fixed charge   : {inr(fixed)}")
print(f"  Duty/tax (~5%) : {inr(duty)}   (varies by state)")
print(f"  Estimated bill : {inr(energy + fixed + duty)}")
print("  Tip: a 1.5 ton AC used 8 h a day is roughly 400 units a month.")
