# keywords: days between, date difference, difference between dates, how many days between, working days, business days, weeks between, between dates, duration between
# desc: Days between two dates (days between 1 jan 2027 and 25 dec 2027)
# category: time
# usage: days between <date> and <date>
# rawargs: full
# patterns: \bdays? between\b ;; \bdate difference\b ;; \b(working|business) days\b ;; \bbetween\b.+\band\b
import datetime, re
from _lib import args_text, fail
from _dates import parse_date
t = re.sub(r"\b(days?|weeks?|working|business|how|many|are|there|between|difference|date|dates|from|of|the)\b", " ", args_text().lower())
parts = [p.strip() for p in re.split(r"\band\b|\bto\b|\buntil\b|\btill\b|\bvs\b|->", t) if p.strip()]
ds = [parse_date(p) for p in parts]
if len(ds) != 2 or None in ds:
    fail("Usage: days between <date> and <date>   e.g. days between 1 jan 2027 and 25 dec 2027")
a, b = sorted(ds)
days = (b - a).days
wd = sum(1 for i in range(days) if (a + datetime.timedelta(days=i)).weekday() < 5)
y = b.year - a.year - ((b.month, b.day) < (a.month, a.day))
mo = (b.month - a.month - (b.day < a.day)) % 12
print(f"{a:%d %b %Y} -> {b:%d %b %Y}")
print(f"  {days:,} days  ({days // 7} weeks {days % 7} days)  =  {y} years {mo} months")
print(f"  {wd:,} working days (Mon-Fri, public holidays not excluded)")
