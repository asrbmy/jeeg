# keywords: timestamp, unix time, epoch, unix epoch, epoch time, convert timestamp, timestamp to date, date to timestamp
# desc: Unix timestamp now, or convert one (unix timestamp 1700000000, or a date)
# category: time
# usage: unix timestamp [number|date]
# rawargs: full
# patterns: \b(unix|epoch)\b
import datetime, re, time
from _lib import args_text, fail
from _dates import parse_date
t = args_text().strip()
m = re.fullmatch(r"-?\d{1,14}(?:\.\d+)?", re.sub(r"\b(unix|timestamp|epoch|time|of|to|date)\b", " ", t.lower()).strip())
if not t or t.lower() in ("now", "unix timestamp", "unix time", "timestamp", "epoch"):
    print(f"Now: {int(time.time())}  ({datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M:%S} UTC)")
elif m:
    v = float(m.group())
    if abs(v) > 1e11: v /= 1000            # milliseconds
    try:
        u = datetime.datetime.fromtimestamp(v, datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        fail("That timestamp is out of range.")
    print(f"{u:%Y-%m-%d %H:%M:%S} UTC   |   local: {u.astimezone():%Y-%m-%d %H:%M:%S %Z}")
else:
    d = parse_date(t.lower().replace("unix", "").replace("timestamp", ""))
    if not d: fail("Give a number (1700000000) or a date (25 dec 2026).")
    print(f"{d:%d %b %Y} 00:00 UTC = {int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp())}")
