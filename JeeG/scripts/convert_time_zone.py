# keywords: meeting time, convert time, time zone converter, time difference, what time will it be in, convert timezone, 9 am in london is what time, meeting planner, schedule across time zones
# desc: Convert a meeting time between places (meeting time 9 am india in london, 3 pm new york to mumbai)
# category: time
# usage: meeting time <time> <place> in <place>[, <place>]
# rawargs: yes
# patterns: \bmeeting (time|planner)\b ;; \b\d{1,2}(:\d{2})?\s*(am|pm)\b.*\b(in|to)\b.*\b(india|ist|london|new york|dubai|tokyo|singapore|sydney|mumbai|delhi|utc|gmt)\b
import datetime, re
from _lib import args_text, fail
from _zones import zone_name
try:
    from zoneinfo import ZoneInfo
except ImportError:
    fail("Time zone data needs Python 3.9+ (Windows: pip install tzdata).")
t = args_text().lower()
t = re.sub(r"\b(meeting|time|convert|what|will|it|be|is|the|planner|at|when|schedule|zone|timezone|difference)\b", " ", t)
m = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", t)
if not m: fail("Usage: meeting time <time> <from place> in <place> [, <place>]   e.g. meeting time 9 am india in london, new york")
hh, mm, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3)
if ap:
    if not 1 <= hh <= 12: fail("With am/pm the hour must be 1-12.")
    hh = hh % 12 + (12 if ap == "pm" else 0)
if hh > 23 or mm > 59: fail("That is not a valid time.")
rest = (t[:m.start()] + " | " + t[m.end():])
rest = re.sub(r"\b(in|to|into|vs|and|for|at)\b|,|&", "|", rest)
parts = [" ".join(p.split()) for p in rest.split("|") if p.strip()]
if len(parts) < 2: fail("Give a starting place and at least one place to convert to, e.g. meeting time 9 am india in london")
src, dests = parts[0], parts[1:]
try:
    zs = zone_name(src)
    if not zs: fail(f"I don't know '{src}'. Try a city (london, new york, mumbai...) or a zone like Asia/Tokyo.")
    z0 = ZoneInfo(zs)
    base = datetime.datetime.combine(datetime.datetime.now(z0).date(), datetime.time(hh, mm), tzinfo=z0)
    print(f"{base:%a %d %b %I:%M %p} in {src.title()} ({base.tzname()})")
    for d in dests:
        zd = zone_name(d)
        if not zd: fail(f"I don't know '{d}'.")
        x = base.astimezone(ZoneInfo(zd))
        diff = (x.date() - base.date()).days
        print(f"  = {x:%a %d %b %I:%M %p} in {d.title()} ({x.tzname()}){'  (next day)' if diff == 1 else '  (previous day)' if diff == -1 else ''}")
except Exception as ex:
    if isinstance(ex, SystemExit): raise
    fail(f"Time zone data is missing here ({ex}). Windows: pip install tzdata")
