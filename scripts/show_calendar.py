# keywords: calendar, month, dates, this month, month view
# desc: Show a month calendar (show calendar march 2027)
# category: time
import calendar, datetime, re
from _lib import args_text, fail
t = args_text().lower()
today = datetime.date.today()
month, year = today.month, today.year
months = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
months.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
for w in re.findall(r"[a-z]+", t):
    if w in months:
        month = months[w]
for n in re.findall(r"\d+", t):
    if len(n) == 4:
        year = int(n)
    elif 1 <= int(n) <= 12 and not any(w in months for w in re.findall(r"[a-z]+", t)):
        month = int(n)
if not 1 <= year <= 9999:
    fail("Year out of range.")
print(calendar.month(year, month))
