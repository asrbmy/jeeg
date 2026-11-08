# keywords: maid log, maid absent, daily service, newspaper log, service summary, milkman, helper attendance
# desc: Keep a daily log for milk, maid, newspaper and similar (milk 1.5 at 60; maid absent 3 nov; milk summary)
# category: home
# usage: <item> <qty> [at <price>] | <item> absent [date] | <item> summary [month]
# rawargs: full
# private: yes
# patterns: \b(milk|maid|cook|driver|newspaper|paper|helper|gardener)\s+(absent|missed|leave|present|summary|log|today|rate|\d) ;; \b(milk|maid|newspaper)\s+(attendance|log)\b ;; \bservice\s+(log|summary)\b
# priority: 3
import datetime, re
from _lib import args_text, fail
from _store import load, save
from _dates import parse_past_date as parse_date
t = args_text().strip().lower()
t = re.sub(r"^(?:log|record|note|add)\s+", "", t)
m = re.match(r"^([a-z][a-z ]{1,20}?)\s+(absent|missed|leave|off|present|summary|total|month|log|history|rate)\b\s*(.*)$", t) or re.match(r"^([a-z][a-z ]{1,20}?)\s+(today|yesterday)?\s*(\d+(?:\.\d+)?)\s*(?:l|litres?|liters?|kg|packets?|pcs|x)?\s*(?:at|@|rate)?\s*(\d+(?:\.\d+)?)?\s*(.*)$", t)
if not m:
    fail("Usage: milk 1.5 at 60      (litres/amount, then price each)\n       maid absent 3 nov\n       milk summary   |   maid summary")
data = load("service_log.json", {})
item = m.group(1).strip()
item = re.sub(r"\b(the|my|daily)\b", "", item).strip() or "item"
rec = data.setdefault(item, {"days": {}, "rate": None})
today = datetime.date.today()
def when(txt):
    txt = re.sub(r"\b(on|today)\b", " ", txt).strip()
    if "yesterday" in txt:
        return today - datetime.timedelta(days=1)
    if not txt:
        return today
    d = parse_date(txt)
    if d is None:
        fail("I could not read the date. Try:  maid absent 3 nov")
    return d
word = m.group(2)
if word in ("summary", "total", "month", "log", "history"):
    ym = (today.year, today.month)
    rest = m.group(3)
    mo = re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s*(\d{4})?", rest)
    if mo:
        ym = (int(mo.group(2)) if mo.group(2) else today.year, ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"].index(mo.group(1)) + 1)
    days = {d: v for d, v in rec["days"].items() if d.startswith(f"{ym[0]}-{ym[1]:02d}")}
    if not days:
        fail(f"Nothing logged for {item} in {datetime.date(ym[0], ym[1], 1):%B %Y}.")
    absent = sorted(d for d, v in days.items() if v.get("absent"))
    qty = sum(v.get("qty", 0) for v in days.values())
    cost = sum(v.get("qty", 0) * (v.get("rate") or rec["rate"] or 0) for v in days.values())
    print(f"{item.title()} - {datetime.date(ym[0], ym[1], 1):%B %Y}: {len(days)} day(s) logged")
    if qty:
        print(f"  Total quantity {qty:g}" + (f", cost {cost:,.2f}" if cost else ""))
    if absent:
        print(f"  Absent {len(absent)} day(s): " + ", ".join(d[8:] for d in absent))
elif word in ("absent", "missed", "leave", "off"):
    d = when(m.group(3))
    rec["days"][d.isoformat()] = {"absent": True}
    save("service_log.json", data)
    print(f"Marked {item} absent on {d:%d %b}.")
elif word == "present":
    d = when(m.group(3))
    rec["days"][d.isoformat()] = {"present": True}
    save("service_log.json", data)
    print(f"Marked {item} present on {d:%d %b}.")
elif word == "rate":
    r = re.search(r"\d+(?:\.\d+)?", m.group(3))
    if not r:
        fail("Usage: milk rate 60")
    rec["rate"] = float(r.group())
    save("service_log.json", data)
    print(f"Default price for {item}: {rec['rate']:g}")
else:
    qty = float(m.group(3))
    rate = float(m.group(4)) if m.group(4) else rec["rate"]
    d = when((m.group(2) or "") + " " + (m.group(5) or ""))
    if not 0 < qty <= 10000:
        fail("Check the quantity.")
    rec["days"][d.isoformat()] = {"qty": qty, "rate": rate}
    if rate:
        rec["rate"] = rate
    save("service_log.json", data)
    print(f"Logged {item} {qty:g}" + (f" at {rate:g} = {qty * rate:,.2f}" if rate else "") + f" for {d:%d %b}.")
