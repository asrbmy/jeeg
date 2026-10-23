# keywords: sunrise, sunset, sun rise, sun set, when does the sun rise, daylight hours, day length, sunrise time, sunset time, golden hour
# desc: Sunrise, sunset and day length for a city (sunrise delhi, sunset mumbai tomorrow)
# category: info
# usage: sunrise [city] [tomorrow|date]
# rawargs: yes
import datetime, re
from _lib import args_text, fail
from _astro import PLACES, sun_times
from _dates import parse_date
try: from zoneinfo import ZoneInfo
except ImportError: fail("Needs Python 3.9+ (Windows: pip install tzdata).")
t = args_text().lower()
day = datetime.date.today()
if "tomorrow" in t: day += datetime.timedelta(days=1)
else:
    d = parse_date(re.sub(r"\b(sunrise|sunset|sun|rise|set|time|times|in|at|for|of|the|today|when|does|is|what|day|length|daylight|hours)\b", " ", t) + " ")
    if d and re.search(r"\d", t): day = d
name = next((n for n in sorted(PLACES, key=len, reverse=True) if n in t), "delhi")
lat, lon, tz = PLACES[name]
try: z = ZoneInfo(tz)
except Exception: fail(f"Time zone data missing for {tz} (Windows: pip install tzdata).")
r, s = sun_times(day, lat, lon)
print(f"{name.title()}, {day:%a %d %b %Y}")
if r is None: print(f"  no sunrise or sunset today ({s})"); raise SystemExit(0)
dl = s - r
print(f"  sunrise {r.astimezone(z):%I:%M %p}   sunset {s.astimezone(z):%I:%M %p}   daylight {dl.seconds // 3600}h {dl.seconds % 3600 // 60}m")
print("  (calculated offline, accurate to about 2 minutes; places: " + ", ".join(sorted(p.title() for p in PLACES if p != "new delhi")[:8]) + "... see _astro.py for the full list)")
