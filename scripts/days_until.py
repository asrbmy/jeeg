# keywords: countdown, days left, how many days, until, date difference, days to
# desc: Days until a date (days until 25 dec 2026)
# category: time
import datetime
from _lib import args_text, fail
from _dates import parse_date
t = args_text()
d = parse_date(t)
if not d:
    fail("Give a date, e.g. days until 25 Dec 2026  (or 2026-12-25, 25/12/2026).")
n = (d - datetime.date.today()).days
if n > 0: print(f"{n} days until {d:%A %d %B %Y}")
elif n == 0: print("That is today.")
else: print(f"{d:%A %d %B %Y} was {-n} days ago.")
