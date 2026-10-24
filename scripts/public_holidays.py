# keywords: public holidays, holidays, national holidays, bank holidays, holiday list, holiday calendar, next holiday, is it a holiday, government holidays
# desc: Public holidays for a country and year (public holidays india 2026, holidays in us)
# category: info
# network: yes
# usage: public holidays [country] [year] | next holiday
# rawargs: yes
import datetime, re
from _lib import args_text, fail
from _net import get
t = args_text().lower()
CC = {"india": "IN", "indian": "IN", "us": "US", "usa": "US", "america": "US", "uk": "GB", "britain": "GB", "england": "GB", "canada": "CA",
      "australia": "AU", "germany": "DE", "france": "FR", "japan": "JP", "singapore": "SG", "uae": "AE", "china": "CN", "italy": "IT",
      "spain": "ES", "brazil": "BR", "mexico": "MX", "russia": "RU", "south africa": "ZA", "new zealand": "NZ", "pakistan": "PK",
      "bangladesh": "BD", "nepal": "NP", "sri lanka": "LK", "netherlands": "NL", "ireland": "IE", "indonesia": "ID", "malaysia": "MY"}
cc = next((v for k, v in sorted(CC.items(), key=lambda x: -len(x[0])) if re.search(r"\b" + k + r"\b", t)), "IN")
m = re.search(r"\b(20\d\d)\b", t)
year = int(m.group(1)) if m else datetime.date.today().year
data = get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/{cc}", timeout=10, as_json=True)
if data is None: fail("Could not fetch holidays (offline?).")
if not isinstance(data, list) or not data: fail(f"No holiday data for {cc} {year}.")
today = datetime.date.today()
upcoming_only = bool(re.search(r"\b(next|upcoming)\b", t))
n = 0
for h in data:
    try: d = datetime.date.fromisoformat(h["date"])
    except (KeyError, ValueError): continue
    if upcoming_only and d < today: continue
    n += 1
    if upcoming_only and n > 5: break
    print(f"  {d:%a %d %b %Y}  {h.get('name', '')}" + (f"  ({h['localName']})" if h.get("localName") and h.get("localName") != h.get("name") else ""))
print(f"{cc} {year}: national holidays only; state or regional holidays can differ. Source: Nager.Date")
