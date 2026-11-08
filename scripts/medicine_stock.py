# keywords: medicine stock, pills left, tablets left, medicine supply, refill medicine, medicine refill, days of medicine left, running out of medicine
# desc: Track how many pills are left and when to refill (medicine stock add metformin 30 2 a day; pills left; medicine refill metformin 60)
# category: health
# usage: medicine stock add <name> <count> [<n> a day] | medicine stock | medicine refill <name> <count>
# rawargs: full
# private: yes
# patterns: \b(medicine|medication|pills?|tablets?)\s+(stock|supply|refill)\b ;; \b(pills?|tablets?)\s+left\b ;; \brefill\s+(my\s+)?(medicine|medication|pills?|tablets?|prescription)\b ;; \brunning\s+out\s+of\s+(medicine|pills?)\b
# priority: 3
import datetime, re
from _lib import args_text, fail
from _store import load, save
t = args_text().strip()
t = re.sub(r"^\s*(?:medicine|medication|pills?|tablets?)\s+(?:stock|supply|left|refill)\b|^\s*(?:how\s+many\s+)?(?:pills?|tablets?|medicine)\s+left\b", lambda m: "refill" if "refill" in m.group(0).lower() else "stock", t, flags=re.I).strip()
t = re.sub(r"^(stock|refill)\b", r"\1", t, flags=re.I)
data = load("medicine_stock.json", {})
today = datetime.date.today()
def left(rec):
    days = (today - datetime.date.fromisoformat(rec["since"])).days
    return max(0.0, rec["count"] - days * rec["per_day"])
low = t.lower()
m = re.match(r"^(?:stock\s+)?(add|set)\s+(.+?)\s+(\d+)(?:\s+(?:with\s+)?(\d+(?:\.\d+)?)\s*(?:a|per|/|each)\s*day)?\s*$", t, re.I) or \
    re.match(r"^(?:stock\s+)?(add|set)\s+(.+?)\s+(\d+)(?:\s+at\s+(\d+(?:\.\d+)?)\s*(?:a|per)?\s*day)?\s*$", t, re.I)
r = re.match(r"^(?:refill|restock)\s+(.+?)\s+(\d+)\s*$", t, re.I)
rm = re.match(r"^(?:stock\s+)?(?:remove|delete)\s+(.+)$", t, re.I)
if m:
    name = m.group(2).strip().lower()[:40]
    cnt = int(m.group(3))
    pd = float(m.group(4)) if m.group(4) else (data.get(name, {}).get("per_day") or 1.0)
    if not (0 < cnt <= 100000 and 0 < pd <= 100):
        fail("Check the numbers (count 1-100000, per day 0-100).")
    data[name] = {"count": cnt, "per_day": pd, "since": today.isoformat()}
    save("medicine_stock.json", data)
    print(f"{name}: {cnt} pills, {pd:g} a day -> lasts about {cnt / pd:.0f} days (until {today + datetime.timedelta(days=int(cnt / pd))}).")
elif r:
    name = r.group(1).strip().lower()
    if name not in data:
        fail(f"No stock for '{name}'. Add it first:  medicine stock add {name} 30 1 a day")
    cnt = int(r.group(2))
    data[name]["count"] = int(left(data[name])) + cnt
    data[name]["since"] = today.isoformat()
    save("medicine_stock.json", data)
    print(f"{name}: refilled. Now {data[name]['count']} pills -> about {data[name]['count'] / data[name]['per_day']:.0f} days.")
elif rm:
    name = rm.group(1).strip().lower()
    if data.pop(name, None) is None:
        fail(f"No stock for '{name}'.")
    save("medicine_stock.json", data)
    print(f"Removed {name}.")
else:
    if not data:
        fail("No medicine stock yet. Add one:  medicine stock add metformin 30 2 a day")
    print("Medicine stock (soonest to run out first):")
    for name, rec in sorted(data.items(), key=lambda kv: left(kv[1]) / kv[1]["per_day"]):
        l = left(rec)
        d = l / rec["per_day"]
        flag = "  <- REFILL NOW" if d < 3 else "  <- refill soon" if d < 7 else ""
        print(f"  {name:<22} {l:>5.0f} pills  ~{d:>4.0f} days (until {today + datetime.timedelta(days=int(d))}){flag}")
