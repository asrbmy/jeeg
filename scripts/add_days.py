# keywords: add days, add weeks, add months, days from now, days ago, weeks from, months after, date after, date before, subtract days, plus days, minus days
# desc: Date arithmetic (add 45 days to 1 jan 2027, 3 months from today, 10 days ago)
# category: time
# usage: add <n> days to <date>
# rawargs: full
# patterns: \d+\s*(day|week|month|year)s?\s*(ago|from|later|after|before|hence)\b ;; \b(add|plus|subtract|minus)\s+\d+\s*(day|week|month|year)
import calendar, datetime, re
from _lib import args_text, fail
from _dates import parse_date
t = args_text().lower()
m = re.search(r"(\d+)\s*(day|week|month|year)s?", t)
if not m: fail("Usage: add <n> days|weeks|months|years to <date>   e.g. add 45 days to 1 jan 2027")
n, unit = int(m.group(1)), m.group(2)
neg = bool(re.search(r"\b(subtract|minus|before|ago|back)\b", t))
rest = (t[:m.start()] + " " + t[m.end():])
rest = re.sub(r"\b(add|plus|subtract|minus|from|to|after|before|ago|back|now|date|what|is|the)\b", " ", rest).strip()
base = parse_date(rest) if rest else datetime.date.today()
if not base: fail("I could not read the date. Try: add 45 days to 1 jan 2027")
if n > 100000: fail("That is too large.")
sign = -1 if neg else 1
if unit in ("day", "week"):
    res = base + datetime.timedelta(days=sign * n * (7 if unit == "week" else 1))
else:
    months = n * (12 if unit == "year" else 1) * sign
    y, mo = divmod(base.year * 12 + base.month - 1 + months, 12)
    if not 1 <= y <= 9998: fail("Date out of range.")
    res = datetime.date(y, mo + 1, min(base.day, calendar.monthrange(y, mo + 1)[1]))
print(f"{base:%a %d %b %Y} {'-' if neg else '+'} {n} {unit}{'s' if n != 1 else ''} = {res:%A, %d %B %Y}")
