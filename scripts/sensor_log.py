# keywords: sensor log, sensor chart, measurement log, record temperature, alert when above, log sensor
# desc: Keep a log of any measurement (log reading temperature 24.5 c), see stats and a chart (show readings temperature), and get alerted past a limit (alert when temperature above 30)
# category: data
# usage: log reading <name> <value> [unit] | show readings <name> | readings chart <name> | alert when <name> above|below <n> | list readings
# rawargs: full
# patterns: ^\s*log\s+(?:a\s+)?reading\b ;; \b(?:show|list|see)\s+(?:the\s+|my\s+)?readings\b(?!\s+list) ;; \breadings?\s+(?:chart|graph|stats)\b ;; ^\s*alert\s+when\s+\w+\s+(?:above|below|over|under)\b
# priority: 4
import re, time
from _lib import args_text, fail, notify
from _store import load, save

text = args_text().strip()
low = text.lower()
data = load("readings.json", {"series": {}, "alerts": {}})
series, alerts = data["series"], data["alerts"]
NAME = r"[a-z][a-z0-9_\-]{0,30}"
CAP = 20000


def need_name(n):
    if not re.fullmatch(NAME, n or ""):
        fail("Use a short name of letters, numbers, - or _ (for example: temperature).")
    return n


m = re.match(rf"^log\s+(?:a\s+)?reading\s+({NAME})\s+(?:of\s+|is\s+|=\s*)?(-?\d+(?:\.\d+)?)\s*([a-z%°]{{0,6}})?\s*$", low)
if m:
    name, val, unit = m.group(1), float(m.group(2)), m.group(3) or ""
    rows = series.setdefault(name, [])
    rows.append([int(time.time()), val])
    del rows[:-CAP]
    if unit:
        data.setdefault("units", {})[name] = unit
    save("readings.json", data)
    u = data.get("units", {}).get(name, "")
    print(f"Logged {name} = {val:g} {u}".rstrip() + f"  ({len(rows)} readings)")
    a = alerts.get(name)
    if a and ((a["dir"] == "above" and val > a["limit"]) or (a["dir"] == "below" and val < a["limit"])):
        msg = f"ALERT: {name} is {val:g}, {a['dir']} your limit of {a['limit']:g}."
        print(msg)
        notify("JeeG alert", msg)
        raise SystemExit(0)
    raise SystemExit(0)
m = re.match(rf"^alert\s+when\s+({NAME})\s+(?:is\s+)?(above|below|over|under)\s+(-?\d+(?:\.\d+)?)\s*$", low)
if m:
    d = {"over": "above", "under": "below"}.get(m.group(2), m.group(2))
    alerts[m.group(1)] = {"dir": d, "limit": float(m.group(3))}
    save("readings.json", data)
    print(f"I will warn you when {m.group(1)} goes {d} {float(m.group(3)):g} (checked each time you log a reading).")
    raise SystemExit(0)
if re.match(r"^(?:readings?\s+list|list\s+readings?|show\s+readings?)\s*$", low):
    if not series:
        fail("No readings yet. Log one:  log reading temperature 24.5 c")
    for n, rows in sorted(series.items()):
        a = alerts.get(n)
        print(f"{n}: {len(rows)} readings, last {rows[-1][1]:g}" + (f", alert {a['dir']} {a['limit']:g}" if a else ""))
    raise SystemExit(0)
m = re.match(rf"^(?:show|see)?\s*(?:the\s+|my\s+)?readings?\s*(chart|graph|stats)?\s*(?:of|for)?\s*({NAME})(?:\s+(today|week|month|all))?\s*$", low) or \
    re.match(rf"^(?:show|see)\s+(?:the\s+|my\s+)?(?:readings?\s+)?(chart|graph|stats)?\s*(?:of|for)?\s*({NAME})\s*readings?(?:\s+(today|week|month|all))?\s*$", low)
if not m:
    fail("Try:  log reading temperature 24.5   |   show readings temperature   |   readings chart temperature   |   alert when temperature above 30")
kind, name, span = m.group(1) or "stats", need_name(m.group(2)), m.group(3) or "all"
rows = series.get(name)
if not rows:
    fail(f"No readings for '{name}'. Log one:  log reading {name} 24.5")
cut = {"today": 86400, "week": 7 * 86400, "month": 30 * 86400}.get(span)
if cut:
    rows = [r for r in rows if r[0] >= time.time() - cut]
    if not rows:
        fail(f"No readings for '{name}' in that period.")
vals = [r[1] for r in rows]
u = data.get("units", {}).get(name, "")
print(f"{name} ({span}): {len(vals)} readings   min {min(vals):g}   avg {sum(vals) / len(vals):.2f}   max {max(vals):g}   last {vals[-1]:g} {u}".rstrip())
if kind in {"chart", "graph"}:
    pts = vals
    if len(pts) > 60:                                  # shrink to 60 columns by averaging buckets
        k = len(pts) / 60
        pts = [sum(pts[int(i * k):int((i + 1) * k) or None]) / max(1, len(pts[int(i * k):int((i + 1) * k) or None])) for i in range(60)]
    lo, hi = min(pts), max(pts)
    span_ = (hi - lo) or 1
    h = 8
    grid = [[" "] * len(pts) for _ in range(h)]
    for x, v in enumerate(pts):
        y = int(round((v - lo) / span_ * (h - 1)))
        grid[h - 1 - y][x] = "*"
    for i, row in enumerate(grid):
        label = f"{hi:>9.2f} |" if i == 0 else f"{lo:>9.2f} |" if i == h - 1 else " " * 10 + "|"
        print(label + "".join(row))
    print(" " * 10 + "+" + "-" * len(pts))
a = alerts.get(name)
if a:
    print(f"Alert: warn when {a['dir']} {a['limit']:g}")
