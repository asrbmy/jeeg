"""Forgiving date parsing (day-first for ambiguous numeric dates). Not a task."""
import datetime
import re

FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%d %B %Y", "%d %b %Y", "%B %d %Y",
           "%b %d %Y", "%B %d, %Y", "%b %d, %Y", "%d %B, %Y", "%d %b, %Y")


def parse_date(text):
    t = re.sub(r"\b(on|the|is|of|date|dob|born|birthday|until|till|to)\b|(?<=\d)(st|nd|rd|th)\b", " ", text, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" ,.")
    low = t.lower()
    today = datetime.date.today()
    if low == "today":
        return today
    if low == "yesterday":
        return today - datetime.timedelta(days=1)
    if low == "tomorrow":
        return today + datetime.timedelta(days=1)
    for f in FORMATS:
        try:
            return datetime.datetime.strptime(t, f).date()
        except ValueError:
            pass
    for f in ("%d %B", "%d %b", "%B %d", "%b %d"):          # no year: next occurrence
        try:
            d = datetime.datetime.strptime(t + f" {today.year}", f + " %Y").date()
            return d if d >= today else d.replace(year=today.year + 1)
        except ValueError:
            pass
    return None
