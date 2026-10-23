# keywords: week number, which week, week of year, day of year, quarter, what week is it, iso week, current week, fiscal quarter
# desc: ISO week number, day of year and quarter (week number, week number 25 dec 2026)
# category: time
# usage: week number [date]
# rawargs: full
# patterns: \bweek number\b ;; \bwhich week\b ;; \bday of (the )?year\b
import datetime
from _lib import args_text
from _dates import parse_date
import re
_t = re.sub(r"\b(what|which|is|the|week|number|of|year|day|quarter|iso|current|this|for|it)\b", " ", args_text().lower()).strip()
d = (parse_date(_t) if _t else None) or datetime.date.today()
iso = d.isocalendar()
print(f"{d:%A, %d %B %Y}: week {iso[1]} of {iso[0]}, day {d.timetuple().tm_yday} of the year, calendar quarter Q{(d.month - 1) // 3 + 1}")
