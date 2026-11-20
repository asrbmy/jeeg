# keywords: meter reading, electricity meter, water meter, gas meter, meter log, units used
# desc: Log meter readings and see use per day (meter add electricity 12450, meter list electricity, meter use electricity)
# category: money
# usage: meter add <name> <reading> | meter list <name> | meter use <name>
# rawargs: full
# patterns: ^\s*meter\s+(add|list|use|usage|remove)\b
# priority: 4
import datetime, re
from _lib import args_text, fail
from _store import load, save
t = re.sub(r"^\s*meter\s*", "", args_text(), flags=re.I).strip()
sub, _, body = t.partition(" "); sub, body = sub.lower(), body.strip()
d = load("meters.json", {})
today = datetime.date.today()
if sub == "add":
    m = re.match(r"^([a-z][a-z ]{1,20}?)\s+(\d+(?:\.\d+)?)\s*$", body, re.I)
    if not m: fail("Usage: meter add <name> <reading>   e.g. meter add electricity 12450")
    n, v = m.group(1).lower().strip(), float(m.group(2))
    lst = d.setdefault(n, [])
    if lst and v < lst[-1]["v"]: fail(f"That is lower than your last reading ({lst[-1]['v']:g}). Meters only go up; check the number.")
    if lst and lst[-1]["d"] == today.isoformat(): lst[-1]["v"] = v
    else: lst.append({"d": today.isoformat(), "v": v})
    if len(d) > 20: fail("That is a lot of meters (limit 20).")
    d[n] = lst[-400:]; save("meters.json", d); print(f"Saved {n}: {v:g} on {today:%d %b %Y}.")
elif sub in {"remove"}:
    if body.lower() not in d: fail("Say which one: " + (", ".join(d) or "(nothing saved yet)"))
    del d[body.lower()]; save("meters.json", d); print(f"Removed {body.lower()}.")
else:
    n = body.lower()
    if n not in d: fail("Say which meter: " + (", ".join(d) or "none yet. Example:  meter add electricity 12450"))
    lst = d[n]
    if sub == "list":
        for a in lst[-15:]: print(f"  {a['d']}  {a['v']:g}")
    else:
        if len(lst) < 2: fail("I need at least two readings to work out use.")
        print(f"{n}: use per day between readings")
        for a, b in zip(lst[-7:-1], lst[-6:]):
            days = max(1, (datetime.date.fromisoformat(b["d"]) - datetime.date.fromisoformat(a["d"])).days)
            print(f"  {a['d']} -> {b['d']}: {b['v'] - a['v']:g} units, {(b['v'] - a['v']) / days:.2f} per day")
        days = max(1, (datetime.date.fromisoformat(lst[-1]["d"]) - datetime.date.fromisoformat(lst[0]["d"])).days)
        print(f"  Overall: {(lst[-1]['v'] - lst[0]['v']) / days:.2f} per day over {days} day(s).")
