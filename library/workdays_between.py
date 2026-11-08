# keywords: working days, workdays, business days, days between weekdays, working days between
# desc: Count working days (Mon-Fri) between two dates (workdays 2026-11-01 to 2026-12-31)
# category: time
# usage: workdays <from date> to <to date>
# rawargs: yes
import datetime
import re
import sys

t = " ".join(sys.argv[1:])
d = re.findall(r"\d{4}-\d{2}-\d{2}", t)
if len(d) != 2:
    sys.exit("Usage: workdays 2026-11-01 to 2026-12-31   (dates as YYYY-MM-DD)")
try:
    a, b = (datetime.date.fromisoformat(x) for x in d)
except ValueError:
    sys.exit("One of those dates does not exist.")
if a > b:
    a, b = b, a
if (b - a).days > 36600:
    sys.exit("Choose dates less than 100 years apart.")
days = (b - a).days + 1
full, rem = divmod(days, 7)
work = full * 5 + sum(1 for i in range(rem) if (a + datetime.timedelta(days=full * 7 + i)).weekday() < 5)
print(f"{a:%d %b %Y} to {b:%d %b %Y} (both days counted): {days} days, {work} working days (Mon-Fri), {days - work} weekend days.")
print("Public holidays are not subtracted.")
