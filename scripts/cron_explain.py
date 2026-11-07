# keywords: cron, cron expression, crontab, cron schedule
# desc: Explain a cron schedule in words (cron 30 9 * * 1-5)
# category: developer
# usage: cron <minute hour day month weekday>
# rawargs: full
# patterns: ^\s*(explain\s+)?(the\s+)?(cron|crontab)\b
# priority: 2
import re
from _lib import args_text, fail
t = re.sub(r"^\W*(?:explain\s+)?(?:the\s+)?(?:cron|crontab)(?:\s+(?:expression|schedule|job))?\s*", "", args_text().strip(), flags=re.I).strip("\"'")
f = t.split()
if len(f) != 5:
    fail("Usage: cron 30 9 * * 1-5   (five fields: minute hour day-of-month month day-of-week)")
names = ["minute", "hour", "day of month", "month", "day of week"]
ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
MON = "January February March April May June July August September October November December".split()
DOW = "Sunday Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()
def label(i, v):
    n = int(v)
    return MON[n - 1] if i == 3 else DOW[n] if i == 4 else str(n)
def part(i, s):
    lo, hi = ranges[i]
    if s == "*":
        return f"every {names[i]}"
    m = re.fullmatch(r"(\*|\d+(?:-\d+)?)/(\d+)", s)
    if m:
        if int(m.group(2)) < 1: fail(f"Bad step in '{s}'.")
        return f"every {m.group(2)} {names[i]}s" + ("" if m.group(1) == "*" else f" within {m.group(1)}")
    out = []
    for p in s.split(","):
        r = re.fullmatch(r"(\d+)(?:-(\d+))?", p)
        if not r or not (lo <= int(r.group(1)) <= hi) or (r.group(2) and not lo <= int(r.group(2)) <= hi):
            fail(f"'{p}' is not valid for the {names[i]} field ({lo}-{hi}).")
        out.append(f"{label(i, r.group(1))} to {label(i, r.group(2))}" if r.group(2) else label(i, r.group(1)))
    return ", ".join(out)
NAMES = {n: str(i) for i, n in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}
NAMES.update({n: str(i) for i, n in enumerate("sun mon tue wed thu fri sat".split())})
f = [re.sub(r"[a-z]{3}", lambda m: NAMES.get(m.group(0), m.group(0)), x.lower()) for x in f]
mi, h, dm, mo, dw = f
if re.fullmatch(r"\d+", mi) and re.fullmatch(r"\d+", h) and 0 <= int(h) <= 23 and 0 <= int(mi) <= 59:
    when = f"At {int(h):02d}:{int(mi):02d}"
elif h == "*" and dm == mo == dw == "*" and re.fullmatch(r"\*/\d+", mi):
    when = f"Every {mi[2:]} minutes"
else:
    when = f"Minute: {part(0, mi)}; hour: {part(1, h)}"
extra = [f"{names[i]}: {part(i, v)}" for i, v in ((2, dm), (3, mo), (4, dw)) if v != "*"]
print(when + (" - " + "; ".join(extra) if extra else ("" if when.startswith("Every") else ", every day")))
