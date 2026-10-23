# keywords: gold price, gold rate, silver price, silver rate, price of gold, bullion, gold rate today, sone ka bhav, 22 carat, 24 carat
# desc: Look up gold or silver rates (gold price, silver price delhi)
# category: search
# usage: gold price [city] | silver price [city]
# rawargs: yes
import re
from _lib import args_text, open_url, search_url
t = args_text().lower()
metal = "silver" if "silver" in t and "gold" not in t else "gold"
place = re.sub(r"\b(gold|silver|price|rate|rates|today|of|in|for|the|current|per|gram|carat|\d+k?)\b", " ", t).strip()
q = f"{metal} rate today" + (f" {place}" if place else " india")
open_url(search_url("https://www.google.com/search?q={q}", q))
