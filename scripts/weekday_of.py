# keywords: what day is, weekday, which day, day of week, day of the week, what weekday, day on, was it a, will it be a
# desc: Which weekday a date falls on (what day is 15 aug 2027)
# category: time
# usage: what day is <date>
# rawargs: full
# patterns: \bwhat (week)?day\b ;; \bwhich day\b ;; \bweekday\b ;; \bday of (the )?week\b
from _lib import args_text, fail
from _dates import parse_date
import re
d = parse_date(re.sub(r"\b(what|which|day|days|is|was|will|be|it|of|the|on|week|weekday|a|date|for)\b", " ", args_text().lower()))
if not d: fail("Usage: what day is <date>   e.g. what day is 15 aug 2027")
print(f"{d:%A, %d %B %Y}  (day {d.timetuple().tm_yday} of the year, ISO week {d.isocalendar()[1]})")
