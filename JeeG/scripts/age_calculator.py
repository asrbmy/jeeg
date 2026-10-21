# keywords: age, birthday, how old, born, date of birth, dob
# desc: Work out an age from a birth date
# category: time
import datetime
from _lib import args_text, fail
from _dates import parse_date
d = parse_date(args_text())
today = datetime.date.today()
if not d or d > today:
    fail("Give a past birth date, e.g. age calculator 14 Aug 2001  (or 2001-08-14).")
y = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
m = (today.month - d.month - (today.day < d.day)) % 12
days = (today - d).days
print(f"Age: {y} years, {m} months  ({days:,} days old)")
nb = d.replace(year=today.year) if not (d.month == 2 and d.day == 29) else datetime.date(today.year, 3, 1)
if nb < today:
    nb = nb.replace(year=today.year + 1) if not (d.month == 2 and d.day == 29) else datetime.date(today.year + 1, 3, 1)
print(f"Next birthday in {(nb - today).days} days")
