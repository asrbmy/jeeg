"""Safe personal-data storage and period parsing. Not a task."""
import calendar
import datetime
import json
import os
import re

from _lib import data_dir, fail


def load(name, default):
    p = data_dir() / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        fail(f"{p} is damaged (not valid JSON). Rename or delete it to start fresh.")


def save(name, data):
    """Atomic write: a crash mid-save can never leave a half-written file."""
    p = data_dir() / name
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, p)


MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})


def period(text):
    """'last month' / 'october 2026' / 'week' / 'today' / 'all' -> (start, end, label). Default: this month."""
    t = text.lower()
    today = datetime.date.today()
    words = re.findall(r"[a-z]+", t)
    if "all" in words:
        return None, None, "all time"
    if "today" in words:
        return today, today, "today"
    if "week" in words:
        return today - datetime.timedelta(days=6), today, "last 7 days"
    y = int(m.group()) if (m := re.search(r"\b(19|20)\d{2}\b", t)) else today.year
    mon = next((MONTHS[w] for w in words if w in MONTHS), None)
    if "last" in words and "month" in words:
        first = today.replace(day=1) - datetime.timedelta(days=1)
        y, mon = first.year, first.month
    elif "year" in words and mon is None:
        return datetime.date(y, 1, 1), datetime.date(y, 12, 31), str(y)
    elif mon is None:
        mon = today.month
    last = calendar.monthrange(y, mon)[1]
    return datetime.date(y, mon, 1), datetime.date(y, mon, last), f"{calendar.month_name[mon]} {y}"
