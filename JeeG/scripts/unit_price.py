# keywords: unit price, which is cheaper, price per kg, price per litre, compare prices, better deal, cheaper pack, best value, price per 100g, compare packs
# desc: Which pack is cheaper per kg or litre (unit price 500g 45 vs 1kg 80)
# category: money
# usage: unit price <qty><unit> <price> vs <qty><unit> <price>
# rawargs: yes
import re
from _lib import args_text, fail
t = args_text().lower().replace(",", "")
t = re.sub(r"\b(unit|price|which|is|cheaper|compare|per|kg|better|deal|rs|rupees?|inr)\b(?!\s*\d)", lambda m: m.group(0) if m.group(0) in ("kg",) else " ", t) if False else t
items = []
for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(kg|kgs|g|gm|gms|gram|grams|l|ltr|litre|litres|liter|liters|ml|pcs?|pieces?|dozen)\b\D{0,12}?(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)", t):
    q, u, p = float(m.group(1)), m.group(2), float(m.group(3))
    base = {"kg": 1000, "kgs": 1000, "g": 1, "gm": 1, "gms": 1, "gram": 1, "grams": 1, "l": 1000, "ltr": 1000, "litre": 1000, "litres": 1000,
            "liter": 1000, "liters": 1000, "ml": 1, "pc": 1, "pcs": 1, "piece": 1, "pieces": 1, "dozen": 12}[u]
    kind = "weight" if u in ("kg", "kgs", "g", "gm", "gms", "gram", "grams") else "volume" if u in ("l", "ltr", "litre", "litres", "liter", "liters", "ml") else "count"
    if q <= 0 or p <= 0: fail("Quantities and prices must be above zero.")
    items.append((kind, q * base, p, f"{m.group(1)} {u} for Rs {m.group(3)}"))
if len(items) < 2: fail("Usage: unit price <qty><unit> <price> vs <qty><unit> <price>   e.g. unit price 500g 45 vs 1kg 80")
if len({i[0] for i in items}) != 1: fail("Compare like with like (all weights, all volumes or all counts).")
kind = items[0][0]
scale, label = {"weight": (1000, "kg"), "volume": (1000, "litre"), "count": (1, "piece")}[kind]
res = sorted(((p / q * scale, d) for _, q, p, d in items))
for v, d in res: print(f"  {d:<28} -> Rs {v:,.2f} per {label}")
best, worst = res[0][0], res[-1][0]
if worst - best < 1e-9: print("Same price per unit.")
else: print(f"Cheapest: {res[0][1]} (saves {100 * (worst - best) / worst:.0f}% per {label} vs the dearest)")
