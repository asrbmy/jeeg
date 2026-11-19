# keywords: calendar file, ics file, make ics, calendar event file, save event calendar, add to calendar file
# desc: Make a .ics calendar event file that opens in any calendar app (calendar file dentist 25 dec 4pm)
# category: lists
# usage: calendar file <title> <date> [time] [for <minutes>]
# rawargs: full
# patterns: \b(calendar|ics)\s+(file|event)\b ;; \bmake\s+(an?\s+)?ics\b
# priority: 4
import datetime, re, uuid
from _lib import args_text, fail, output_dir, open_path
from _dates import parse_date
t = re.sub(r"\b(?:make|an?|calendar|ics|file|event)\b", " ", args_text(), flags=re.I).strip()
dur = 60
m = re.search(r"\bfor\s+(\d{1,4})\s*(?:min\w*)?\s*$", t, re.I)
if m: dur = int(m.group(1)); t = t[:m.start()].strip()
tm = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b|\b([01]?\d|2[0-3]):([0-5]\d)\b", t, re.I)
hh = mm = None
if tm:
    if tm.group(3):
        hh = int(tm.group(1)) % 12 + (12 if tm.group(3).lower() == "pm" else 0); mm = int(tm.group(2) or 0)
    else: hh, mm = int(tm.group(4)), int(tm.group(5))
    t = (t[:tm.start()] + " " + t[tm.end():]).strip()
words = t.split(); title = d = None
for i in range(1, len(words)):
    d = parse_date(" ".join(words[i:]))
    if d: title = " ".join(words[:i]); break
if not title or not d: fail("Usage: calendar file <title> <date> [time] [for <minutes>]   e.g. calendar file dentist 25 dec 4pm")
if hh is not None and not 0 <= hh <= 23: fail("That time is not valid.")
esc = lambda s: s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
if hh is None:
    ev = [f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{d + datetime.timedelta(days=1):%Y%m%d}"]
else:
    s = datetime.datetime.combine(d, datetime.time(hh, mm)); e = s + datetime.timedelta(minutes=dur)
    ev = [f"DTSTART:{s:%Y%m%dT%H%M%S}", f"DTEND:{e:%Y%m%dT%H%M%S}"]
lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//JeeG//EN", "BEGIN:VEVENT", f"UID:{uuid.uuid4()}@jeeg", f"DTSTAMP:{stamp}", *ev, f"SUMMARY:{esc(title)}", "END:VEVENT", "END:VCALENDAR"]
slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:30] or "event"
p = output_dir("JeeG calendar") / f"{slug}-{d:%Y%m%d}.ics"
p.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
print(f"Made {p} ({title}, {d:%d %b %Y}" + (f" {hh:02d}:{mm:02d}" if hh is not None else ", all day") + "). Open it to add it to your calendar.")
