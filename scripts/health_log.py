# keywords: bp log, blood pressure, blood sugar, glucose log, sugar reading, health summary, bp reading, diabetes log
# desc: Log blood pressure and blood sugar, see a weekly summary (bp 120/80; sugar 105 fasting; health summary)
# category: health
# usage: bp <sys>/<dia> | sugar <value> [fasting|after meal] | health summary [month]
# rawargs: full
# private: yes
# patterns: \bbp\s+\d{2,3}\s*/\s*\d{2,3}\b ;; \b(blood\s+pressure|bp)\s+(log|reading|summary)\b ;; \b(blood\s+)?(sugar|glucose)\s+(\d|reading|log|summary) ;; \bhealth\s+summary\b ;; \blog\s+(my\s+)?(bp|blood\s+(pressure|sugar))\b
# priority: 3
import datetime, re, time
from _lib import args_text, fail
from _store import load, save
t = args_text().strip()
low = t.lower()
log = load("health_log.json", [])
now = int(time.time())
if re.search(r"\b(clear|delete|erase)\b.*\b(log|readings|health)\b|^\s*(clear|delete)\b", low):
    save("health_log.json", [])
    print("Health log cleared.")
    raise SystemExit(0)
bp = re.search(r"(\d{2,3})\s*(?:/|over)\s*(\d{2,3})(?:\D+(\d{2,3})\s*(?:bpm|pulse|hr))?", low)
sg = re.search(r"(?:sugar|glucose)\D{0,12}?(\d+(?:\.\d+)?)", low) or re.search(r"(\d+(?:\.\d+)?)\s*(?:mg/dl|mmol)", low)
if bp and not re.search(r"\bsummary|week\b", low):
    s, d = int(bp.group(1)), int(bp.group(2))
    if not (60 <= s <= 260 and 30 <= d <= 160 and s > d):
        fail("Check the reading: systolic 60-260 and diastolic 30-160, like  bp 120/80")
    log.append({"t": now, "k": "bp", "a": s, "b": d, "p": int(bp.group(3)) if bp.group(3) else None})
    save("health_log.json", log[-2000:])
    cat = "low" if s < 90 or d < 60 else "normal" if s < 120 and d < 80 else "elevated" if s < 130 and d < 80 else "high (stage 1)" if s < 140 and d < 90 else "high (stage 2)" if s < 180 and d < 120 else "VERY HIGH - get medical help"
    print(f"Saved BP {s}/{d}: {cat}.  (General ranges, not a diagnosis.)")
elif sg and not re.search(r"\bsummary|week\b", low):
    v = float(sg.group(1))
    mmol = v < 35
    if not (1 <= v <= 1500):
        fail("Check the number, like  sugar 105 fasting   (mg/dL) or  sugar 5.8 fasting   (mmol/L)")
    mgdl = v * 18 if mmol else v
    ctx = "fasting" if "fast" in low else "after meal" if re.search(r"after|post|pp\b|meal", low) else "random"
    log.append({"t": now, "k": "sugar", "a": v, "u": "mmol/L" if mmol else "mg/dL", "c": ctx})
    save("health_log.json", log[-2000:])
    note = "low" if mgdl < 70 else ("normal" if mgdl < 100 else "above normal" if mgdl < 126 else "high") if ctx == "fasting" else ("normal" if mgdl < 140 else "above normal" if mgdl < 200 else "high") if ctx == "after meal" else "noted"
    print(f"Saved sugar {v:g} {'mmol/L' if mmol else 'mg/dL'} ({ctx}): {note}.  (General ranges, not a diagnosis.)")
else:
    days = 30 if re.search(r"\bmonth|30\b", low) else 7
    since = now - days * 86400
    rows = [x for x in log if x["t"] >= since]
    if not rows:
        fail("No readings yet. Log one:  bp 120/80   or   sugar 105 fasting")
    print(f"Health summary, last {days} days ({len(rows)} readings):")
    b = [x for x in rows if x["k"] == "bp"]
    if b:
        print(f"  Blood pressure: {len(b)} reading(s), average {sum(x['a'] for x in b) / len(b):.0f}/{sum(x['b'] for x in b) / len(b):.0f}, "
              f"highest {max(x['a'] for x in b)}/{max(x['b'] for x in b)}, lowest {min(x['a'] for x in b)}/{min(x['b'] for x in b)}")
    for ctx in ("fasting", "after meal", "random"):
        s = [x["a"] * (18 if x["u"] == "mmol/L" else 1) for x in rows if x["k"] == "sugar" and x["c"] == ctx]
        if s:
            print(f"  Sugar ({ctx}): {len(s)} reading(s), average {sum(s) / len(s):.0f} mg/dL, highest {max(s):.0f}, lowest {min(s):.0f}")
    print("  Recent:")
    for x in rows[-6:]:
        when = time.strftime("%d %b %H:%M", time.localtime(x["t"]))
        print(f"    {when}  " + (f"BP {x['a']}/{x['b']}" + (f"  pulse {x['p']}" if x.get('p') else "") if x["k"] == "bp" else f"sugar {x['a']:g} {x['u']} ({x['c']})"))
    print("  Show this to your doctor; do not change medicine because of a number here.")
