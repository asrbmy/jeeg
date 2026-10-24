# keywords: convert, conversion, converter, unit, units, currency, exchange, how many, in miles, in km, kg to lb, celsius, fahrenheit
# desc: Convert units offline (convert 5 km to miles, 100 f to c); falls back to Google for currency
# category: utility
# network: yes
# usage: convert <n> <unit> to <unit>
# rawargs: yes
import re, urllib.parse, webbrowser
from _lib import args_text, fail
text = args_text().lower().replace(",", "")
m = re.search(r"(-?\d+(?:\.\d+)?)\s*([a-z°/ ]+?)\s+(?:to|in|into|as)\s+([a-z°/ ]+)$", text)
if not m:
    fail("Usage: convert <number> <unit> to <unit>   e.g. convert 5 km to miles")
val, a, b = float(m.group(1)), m.group(2).strip(), m.group(3).strip()
def key(u):
    u = u.replace("°", "").strip()
    for pre in ("square ", "us "):
        u = u.removeprefix(pre)
    return u[:-1] if len(u) > 3 and u.endswith("s") and u not in ("celsius", "kmps") else u
L = lambda f, *n: {x: ("length", f) for x in n}
U = {}
U.update(L(1, "m", "meter", "metre")); U.update(L(1000, "km", "kilometer", "kilometre", "kms"))
U.update(L(0.01, "cm", "centimeter", "centimetre")); U.update(L(0.001, "mm", "millimeter", "millimetre"))
U.update(L(1609.344, "mile", "mi")); U.update(L(0.3048, "ft", "foot", "feet")); U.update(L(0.0254, "inch", "in"))
U.update(L(0.9144, "yard", "yd")); U.update(L(1852, "nautical mile", "nmi"))
M = lambda f, *n: {x: ("mass", f) for x in n}
U.update(M(1, "kg", "kilogram", "kilo")); U.update(M(0.001, "g", "gram")); U.update(M(1e-6, "mg", "milligram"))
U.update(M(0.45359237, "lb", "pound", "lbs")); U.update(M(0.028349523125, "oz", "ounce")); U.update(M(1000, "tonne", "ton", "metric ton"))
U.update(M(6.35029318, "stone", "st"))
V = lambda f, *n: {x: ("volume", f) for x in n}
U.update(V(1, "l", "liter", "litre")); U.update(V(0.001, "ml", "milliliter", "millilitre")); U.update(V(3.785411784, "gallon", "gal"))
U.update(V(0.2365882365, "cup")); U.update(V(0.0147867648, "tbsp", "tablespoon")); U.update(V(0.00492892159, "tsp", "teaspoon"))
U.update(V(0.0295735296, "fl oz", "fluid ounce")); U.update(V(0.473176473, "pint", "pt")); U.update(V(0.946352946, "quart", "qt"))
S = lambda f, *n: {x: ("speed", f) for x in n}
U.update(S(1, "m/s", "mps")); U.update(S(1 / 3.6, "km/h", "kmh", "kph", "kmph")); U.update(S(0.44704, "mph", "mile/h"))
U.update(S(0.514444, "knot", "kn", "kt"))
D = lambda f, *n: {x: ("data", f) for x in n}
U.update(D(1, "b", "byte")); U.update(D(1024, "kb", "kilobyte")); U.update(D(1024 ** 2, "mb", "megabyte"))
U.update(D(1024 ** 3, "gb", "gigabyte")); U.update(D(1024 ** 4, "tb", "terabyte")); U.update(D(1024 ** 5, "pb", "petabyte"))
T = lambda f, *n: {x: ("time", f) for x in n}
U.update(T(1, "s", "sec", "second")); U.update(T(60, "min", "minute")); U.update(T(3600, "h", "hr", "hour"))
U.update(T(86400, "day", "d")); U.update(T(604800, "week", "wk")); U.update(T(31557600, "year", "yr"))
A = lambda f, *n: {x: ("area", f) for x in n}
U.update(A(1, "sq m", "m2", "m^2", "sqm")); U.update(A(1e6, "sq km", "km2", "km^2")); U.update(A(0.09290304, "sq ft", "ft2", "sqft"))
U.update(A(4046.8564224, "acre")); U.update(A(10000, "hectare", "ha")); U.update(A(2589988.110336, "sq mile", "mi2"))
ka, kb = key(a), key(b)
temp = {"c": "c", "celsius": "c", "f": "f", "fahrenheit": "f", "k": "k", "kelvin": "k"}
if ka in temp and kb in temp:
    x, y = temp[ka], temp[kb]
    c = val if x == "c" else (val - 32) * 5 / 9 if x == "f" else val - 273.15
    r = c if y == "c" else c * 9 / 5 + 32 if y == "f" else c + 273.15
    print(f"{val:g} {a} = {r:.4g} {b}")
elif ka in U and kb in U and U[ka][0] == U[kb][0]:
    r = val * U[ka][1] / U[kb][1]
    print(f"{val:g} {a} = {r:,.6g} {b}" + ("   (1 KB = 1024 B)" if U[ka][0] == "data" else ""))
elif ka in U and kb in U:
    fail(f"Cannot convert {U[ka][0]} to {U[kb][0]}.")
else:
    from _money import currency_cli
    if currency_cli(text):
        raise SystemExit(0)
    print("Not a known unit pair - searching Google...")
    webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(f"convert {val:g} {a} to {b}"))
