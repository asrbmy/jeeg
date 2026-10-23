# keywords: cooking convert, cup to grams, grams to cups, tablespoon to ml, teaspoon to ml, recipe conversion, convert cups, cooking measures, how many grams in a cup, baking conversion
# desc: Convert cooking measures, with grams for common ingredients (cooking convert 2 cups flour to grams)
# category: utility
# usage: cooking convert <amount> <unit> [ingredient] to <unit>
# rawargs: yes
import re
from _lib import args_text, fail
t = args_text().lower()
m = re.search(r"(\d+(?:\.\d+)?|\d+/\d+|\d+\s+\d+/\d+)\s*(cups?|tbsp|tablespoons?|tsp|teaspoons?|ml|l|litres?|liters?|oz|ounces?|g|grams?|kg)\b", t)
if not m: fail("Usage: cooking convert <amount> <unit> [ingredient] to <unit>   e.g. cooking convert 2 cups flour to grams")
a = m.group(1)
if "/" in a:
    p = a.split(); fr = p[-1].split("/"); a = (int(p[0]) if len(p) > 1 else 0) + int(fr[0]) / int(fr[1])
a = float(a)
U = {"cup": 236.588, "cups": 236.588, "tbsp": 14.7868, "tablespoon": 14.7868, "tablespoons": 14.7868, "tsp": 4.92892, "teaspoon": 4.92892,
     "teaspoons": 4.92892, "ml": 1.0, "l": 1000.0, "litre": 1000.0, "litres": 1000.0, "liter": 1000.0, "liters": 1000.0}
W = {"g": 1.0, "gram": 1.0, "grams": 1.0, "kg": 1000.0, "oz": 28.3495, "ounce": 28.3495, "ounces": 28.3495}
GPML = {"water": 1.0, "milk": 1.03, "oil": 0.92, "ghee": 0.91, "butter": 0.96, "honey": 1.42, "flour": 0.53, "maida": 0.53, "atta": 0.55, "sugar": 0.85,
        "powdered sugar": 0.51, "icing sugar": 0.51, "rice": 0.78, "oats": 0.38, "cocoa": 0.42, "curd": 1.03, "yogurt": 1.03, "salt": 1.22}
ing = next((k for k in sorted(GPML, key=len, reverse=True) if k in t), None)
rest = t[m.end():]
to = re.search(r"\b(?:to|in|into)\s+(cups?|tbsp|tablespoons?|tsp|teaspoons?|ml|l|litres?|liters?|oz|ounces?|g|grams?|kg)\b", rest)
if not to: fail("Say what to convert to, e.g. ... to grams / to ml / to cups")
src, dst = m.group(2), to.group(1)
def to_base(v, u):               # -> ("vol" ml | "wt" g)
    if u in U: return "vol", v * U[u]
    return "wt", v * W[u]
kind, base = to_base(a, src)
if dst in U: tk, scale = "vol", U[dst]
else: tk, scale = "wt", W[dst]
if kind != tk:
    if not ing: fail("Converting between volume and weight needs an ingredient: " + ", ".join(sorted(GPML)))
    base = base * GPML[ing] if kind == "vol" else base / GPML[ing]
res = base / scale
print(f"{a:g} {src}" + (f" {ing}" if ing else "") + f" = {res:,.1f} {dst}" if res >= 10 else f"{a:g} {src}" + (f" {ing}" if ing else "") + f" = {res:,.2f} {dst}")
if kind != tk: print("(approximate: ingredient weights vary with brand and how it is packed; US cup = 236.6 ml)")
