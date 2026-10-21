# keywords: exchange rates, rupee rate, forex rates, dollar rate, currency rates, rupee vs dollar, usd to inr rate, today's rates, rate table
# desc: Table of today's exchange rates against the rupee (exchange rates, exchange rates eur)
# category: money
# usage: exchange rates [base currency]
# rawargs: yes
import re
from _lib import args_text, fail
from _net import get
t = args_text().lower()
base = "INR"
m = re.search(r"\b(usd|eur|gbp|aed|sgd|jpy|aud|cad|chf|cny|sar|inr)\b", t)
if m: base = m.group(1).upper()
data = get(f"https://open.er-api.com/v6/latest/{base}", timeout=8, as_json=True)
if not data or data.get("result") != "success": fail("Could not fetch live exchange rates (offline?).")
rates = data["rates"]
others = [c for c in ("USD", "EUR", "GBP", "AED", "SGD", "JPY", "AUD", "CAD", "CHF", "CNY", "SAR", "INR") if c != base]
print(f"Value of 1 unit of each currency in {base} (live, updated {data.get('time_last_update_utc', '?')[:16]}):")
for c in others:
    r = rates.get(c)
    if r: print(f"  1 {c} = {1 / r:,.4f} {base}")
