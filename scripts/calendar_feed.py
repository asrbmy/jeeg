# keywords: calendar feed, ics, ical, upcoming events, google calendar feed, calendar events from link, agenda from calendar
# desc: Show upcoming events from a calendar link or .ics file (calendar feed add work <secret iCal address>, calendar feed upcoming). Works with Google/Outlook secret iCal links, no sign-in.
# category: reminders
# usage: calendar feed add <name> <https address | file.ics> | calendar feed upcoming [name] [days] | calendar feed list | calendar feed remove <name>
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*calendar\s+feeds?\b ;; \b(ics|ical)\b
# priority: 4
import datetime, re, urllib.error, urllib.request
from pathlib import Path
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name, check_url, mask_url
t = re.sub(r"^\s*calendar\s+feeds?\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 2)
cmd = parts[0].lower() if parts else "upcoming"
reg = load_reg("ics")


def fetch(src):
    if re.match(r"https?://", src):
        check_url(src)
        try:
            with urllib.request.urlopen(urllib.request.Request(src, headers={"User-Agent": "JeeG"}), timeout=20) as r:
                return r.read(5_000_000).decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as ex:
            fail(f"Could not read the calendar: {getattr(ex, 'reason', ex)}")
    p = Path(src).expanduser()
    if not p.is_file() or p.stat().st_size > 5_000_000:
        fail("Give an https address or an .ics file under 5 MB.")
    return p.read_text(encoding="utf-8", errors="replace")


def parse_dt(v):
    v = v.strip()
    try:
        if re.fullmatch(r"\d{8}", v):
            return datetime.datetime.strptime(v, "%Y%m%d"), True
        if v.endswith("Z"):
            d = datetime.datetime.strptime(v, "%Y%m%dT%H%M%SZ").replace(tzinfo=datetime.timezone.utc)
            return d.astimezone().replace(tzinfo=None), False
        return datetime.datetime.strptime(v[:15], "%Y%m%dT%H%M%S"), False
    except ValueError:
        return None, False


def events(text):
    text = re.sub(r"\r?\n[ \t]", "", text)                      # unfold long lines
    for blk in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", text, re.S):
        f = {}
        for ln in blk.strip().splitlines():
            k, _, v = ln.partition(":")
            f.setdefault(k.split(";")[0].upper(), v)
        d, allday = parse_dt(f.get("DTSTART", ""))
        if d:
            yield d, allday, (f.get("SUMMARY") or "(no title)").replace("\\,", ",").replace("\\n", " ")[:80], "RRULE" in f


if cmd == "list":
    print("Saved calendars:" if reg else "None saved. Add one:  calendar feed add work https://calendar.google.com/calendar/ical/.../basic.ics")
    for k, v in sorted(reg.items()):
        print(f"  {k:<12} {mask_url(v) if v.startswith('http') else v}")
elif cmd == "add":
    if len(parts) < 3:
        fail("Usage: calendar feed add <name> <https address | file.ics>")
    src = parts[2].strip()
    if "BEGIN:VCALENDAR" not in fetch(src)[:5000].upper():
        fail("That does not look like a calendar (.ics) file or link.")
    reg[clean_name(parts[1])] = src
    save_reg("ics", reg)
    print("Saved. The address is kept private. Try:  calendar feed upcoming")
elif cmd in {"remove", "delete"}:
    if reg.pop(clean_name(parts[1] if len(parts) > 1 else ""), None) is None:
        fail("No calendar with that name.")
    save_reg("ics", reg)
    print("Removed.")
elif cmd == "upcoming":
    if not reg:
        fail("No calendar saved yet. Add one:  calendar feed add work <address>")
    rest = parts[1:]
    days = 7
    names = []
    for w in " ".join(rest).split():
        if w.isdigit():
            days = max(1, min(90, int(w)))
        else:
            names.append(w.lower())
    pick = [n for n in names if n in reg] or sorted(reg)
    now = datetime.datetime.now()
    end = now + datetime.timedelta(days=days)
    rows, repeating = [], False
    for n in pick:
        src = reg[n]
        for d, allday, title, rep in events(fetch(src)):
            if (d.replace(hour=23, minute=59) if allday else d) >= now and d <= end:
                rows.append((d, allday, title, n))
            repeating = repeating or rep
    rows.sort()
    print(f"Next {days} day(s):" if rows else f"Nothing in the next {days} day(s).")
    for d, allday, title, n in rows[:40]:
        print(f"  {d:%a %d %b}  {'all day' if allday else f'{d:%H:%M}':<8} {title}" + (f"   [{n}]" if len(pick) > 1 else ""))
    if repeating:
        print("(Repeating events show only on their first date; this simple reader does not expand repeats.)")
else:
    fail("Use:  calendar feed add | upcoming | list | remove")
