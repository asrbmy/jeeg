# keywords: sleep log, log sleep, i slept, hours of sleep, sleep tracker, sleep hours, sleep show, my sleep, track sleep
# desc: Log how long you slept and see your recent average (sleep log 7.5 hours, sleep show)
# category: health
# usage: sleep log <hours> | sleep show
# rawargs: yes
import datetime, re
from _lib import args_text, fail
from _store import load, save
t = args_text().lower()
s = load("sleep.json", {})
m = re.search(r"(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hours?)?(?:\s*(\d+)\s*(?:m|min|mins|minutes?))?", t)
if m and not re.search(r"\b(show|history|average)\b", t):
    h = float(m.group(1)) + (int(m.group(2)) / 60 if m.group(2) else 0)
    if not 0 < h <= 24: fail("Sleep must be between 0 and 24 hours.")
    day = (datetime.date.today() - datetime.timedelta(days=1 if "last night" in t else 0)).isoformat()
    s[day] = round(h, 2); save("sleep.json", s)
    print(f"Logged {h:.1f} hours for {day}.")
last = sorted(s.items())[-7:]
if last:
    print("Recent nights: " + ", ".join(f"{d[5:]} {v:g}h" for d, v in last))
    print(f"Average of these {len(last)}: {sum(v for _, v in last) / len(last):.1f} h")
else: print("No sleep logged yet. Example:  sleep log 7.5 hours")
