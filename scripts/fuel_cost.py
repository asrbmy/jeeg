# keywords: fuel cost, petrol cost, diesel cost, trip cost, mileage calculator, fuel calculator, how much petrol, travel cost, cost of trip, kmpl
# desc: Trip fuel cost from distance, mileage and price (fuel cost 250 km 18 kmpl 105 per litre)
# category: money
# usage: fuel cost <km> km <mileage> kmpl <price>
# rawargs: yes
import re
from _lib import args_text, fail
from _money import inr
t = args_text().lower().replace(",", "")
mi = re.search(r"(\d+(?:\.\d+)?)\s*(?:kmpl|km/l|km per l\w*|mileage)", t) or re.search(r"(?:mileage|kmpl)\s*(?:of|is)?\s*(\d+(?:\.\d+)?)", t)
t2 = t.replace(mi.group(0), " ") if mi else t
di = re.search(r"(\d+(?:\.\d+)?)\s*(?:km|kms|kilomet\w+)\b", t2)
t3 = t2.replace(di.group(0), " ") if di else t2
pr = re.search(r"(?:rs\.?|inr|₹|price|@|at)\s*(\d+(?:\.\d+)?)", t3) or re.search(r"(\d+(?:\.\d+)?)\s*(?:rs|rupees?|per\s*l\w*|/l)\b", t3) or re.search(r"(\d+(?:\.\d+)?)", t3)
if not (mi and di and pr): fail("Usage: fuel cost <distance> km <mileage> kmpl <price per litre>   e.g. fuel cost 250 km 18 kmpl 105")
d, m, p = float(di.group(1)), float(mi.group(1)), float(pr.group(1))
if m <= 0 or d <= 0 or p <= 0: fail("All numbers must be above zero.")
lit = d / m
print(f"{d:,.0f} km at {m:g} km/l uses {lit:,.2f} litres.")
print(f"Fuel cost at Rs {p:g}/litre: Rs {inr(lit * p)}   (Rs {p / m:,.2f} per km)")
print("Round trip: Rs " + inr(2 * lit * p))
