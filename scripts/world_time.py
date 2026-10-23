# keywords: time in, world clock, timezone, time zone, current time in, clock in, what time in, time at, local time, time difference
# desc: Current time in cities (time in london, tokyo and new york)
# category: time
# usage: time in <city>[, <city>]
# rawargs: full
# patterns: \btime (in|at)\b ;; \bwhat time is it in\b ;; \bworld (clock|time)\b
import datetime, re, webbrowser
from _lib import args_text, fail
CITY = {"london": "Europe/London", "paris": "Europe/Paris", "berlin": "Europe/Berlin", "madrid": "Europe/Madrid", "rome": "Europe/Rome",
 "moscow": "Europe/Moscow", "istanbul": "Europe/Istanbul", "dubai": "Asia/Dubai", "abu dhabi": "Asia/Dubai", "riyadh": "Asia/Riyadh",
 "mumbai": "Asia/Kolkata", "delhi": "Asia/Kolkata", "new delhi": "Asia/Kolkata", "kolkata": "Asia/Kolkata", "bangalore": "Asia/Kolkata",
 "bengaluru": "Asia/Kolkata", "chennai": "Asia/Kolkata", "hyderabad": "Asia/Kolkata", "india": "Asia/Kolkata", "karachi": "Asia/Karachi",
 "dhaka": "Asia/Dhaka", "kathmandu": "Asia/Kathmandu", "colombo": "Asia/Colombo", "bangkok": "Asia/Bangkok", "singapore": "Asia/Singapore",
 "hong kong": "Asia/Hong_Kong", "beijing": "Asia/Shanghai", "shanghai": "Asia/Shanghai", "tokyo": "Asia/Tokyo", "japan": "Asia/Tokyo", "seoul": "Asia/Seoul",
 "sydney": "Australia/Sydney", "melbourne": "Australia/Melbourne", "auckland": "Pacific/Auckland", "cairo": "Africa/Cairo",
 "nairobi": "Africa/Nairobi", "lagos": "Africa/Lagos", "johannesburg": "Africa/Johannesburg", "new york": "America/New_York",
 "washington": "America/New_York", "toronto": "America/Toronto", "chicago": "America/Chicago", "denver": "America/Denver",
 "los angeles": "America/Los_Angeles", "san francisco": "America/Los_Angeles", "seattle": "America/Los_Angeles",
 "mexico city": "America/Mexico_City", "sao paulo": "America/Sao_Paulo", "utc": "UTC", "gmt": "UTC"}
t = re.sub(r"\b(what|is|it|the|current|time|now|in|at|clock|local|world|show|of|tell|me)\b", " ", args_text().lower())
names = [n.strip() for n in re.split(r",|\band\b|&", t) if n.strip()]
if not names:
    names = ["utc", "new york", "london", "dubai", "mumbai", "singapore", "tokyo", "sydney"]
try:
    from zoneinfo import ZoneInfo
    ZoneInfo("UTC")
except Exception:
    ZoneInfo = None
now = datetime.datetime.now(datetime.timezone.utc)
for n in names:
    zone = CITY.get(n) or (n.replace(" ", "_").title() if "/" in n else None)
    if not zone:
        fail(f"I don't know '{n}'. Try a major city (london, tokyo, new york...) or a zone like Asia/Tokyo.")
    if ZoneInfo is None:
        webbrowser.open("https://time.is/" + n.replace(" ", "_"))
        fail("Time zone data is missing here (Windows: pip install tzdata) - opened time.is instead.")
    try:
        z = now.astimezone(ZoneInfo(zone))
    except Exception:
        fail(f"No time zone data for {zone} (Windows: pip install tzdata).")
    print(f"{n.title():<14}{z:%a %d %b  %I:%M %p}   ({z.tzname()}, UTC{z:%z})")
