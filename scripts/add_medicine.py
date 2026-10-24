# keywords: add medicine, medicine schedule, save medicine, new medicine, pill schedule, tablet times, add pill
# desc: Save a medicine and its times (add medicine metformin at 8am and 8pm)
# category: health
# usage: add medicine <name> at <time> [and <time>]
# rawargs: yes
# private: yes
# patterns: \badd\s+(a\s+)?(medicine|medication|pill|tablet)\b ;; \b(medicine|pill|tablet)\s+schedule\b
# priority: 2
import re
from _lib import args_text, fail
from _store import load, save
t = args_text()
t = re.sub(r"^\s*(?:please\s+)?(?:add|save|new|set)?\s*(?:a\s+)?(?:medicine|medication|pill|tablet)s?\s*", "", t, flags=re.I)
times = re.findall(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b|\b([01]?\d|2[0-3]):([0-5]\d)\b", t, re.I)
if not times:
    fail("Usage: add medicine <name> at <time> [and <time>]   e.g. add medicine metformin at 8am and 8pm")
out = []
for h, mi, ap, h24, m24 in times:
    if ap:
        hh = int(h) % 12 + (12 if ap.lower() == "pm" else 0); mm = int(mi or 0)
        if not 1 <= int(h) <= 12 or mm > 59: fail("Check the times.")
    else:
        hh, mm = int(h24), int(m24)
    out.append(f"{hh:02d}:{mm:02d}")
name = re.sub(r"\b(at|and|every|day|daily|morning|night|evening|noon)\b|\b\d{1,2}(?::\d{2})?\s*(?:am|pm)?\b|[,;]", " ", t, flags=re.I).split()
name = " ".join(name).lower()[:40]
if not name: fail("Give the medicine a name.")
if len(set(out)) > 8: fail("At most 8 times a day.")
med = load("medicines.json", {})
med[name] = {"times": sorted(set(out)), "taken": med.get(name, {}).get("taken", {})}
save("medicines.json", med)
print(f"Saved {name}: " + ", ".join(med[name]["times"]) + ".  Say 'medicine today' to see it, 'medicine remind' to get alerts today.")
