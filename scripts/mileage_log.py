# keywords: mileage, km log, trip log, distance log, mileage report, travel claim
# desc: Log trips and work out what you can claim (mileage add 25 km office, mileage report, mileage rate 8)
# category: money
# usage: mileage add <km> [note] | mileage report [month] | mileage rate <per km>
# rawargs: full
# patterns: ^\s*mileage\b
# priority: 4
import datetime, re
from _lib import args_text, fail
from _store import load, save
from _money import inr
t = re.sub(r"^\s*mileage\s*", "", args_text(), flags=re.I).strip()
sub, _, body = t.partition(" "); sub, body = sub.lower(), body.strip()
d = load("mileage.json", {"rate": 0, "trips": []})
if sub == "rate":
    m = re.match(r"^\D*(\d+(?:\.\d+)?)", body)
    if not m or not 0 < float(m.group(1)) < 1000: fail("Usage: mileage rate <amount per km>")
    d["rate"] = float(m.group(1)); save("mileage.json", d); print(f"Rate set to {inr(d['rate'])} per km.")
elif sub == "add":
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:km|kms|kilometres?|kilometers?)?\s*(.*)$", body, re.I)
    if not m or not 0 < float(m.group(1)) <= 5000: fail("Usage: mileage add <km> [note]   e.g. mileage add 25 km office")
    d["trips"].append({"date": datetime.date.today().isoformat(), "km": float(m.group(1)), "note": m.group(2)[:60]}); d["trips"] = d["trips"][-5000:]
    save("mileage.json", d); print(f"Logged {float(m.group(1)):g} km." + ("" if d["rate"] else " Set a claim rate with:  mileage rate 8"))
else:
    mo = datetime.date.today().strftime("%Y-%m")
    tr = [x for x in d["trips"] if x["date"].startswith(mo)]
    if not tr: fail("No trips logged this month. Example:  mileage add 25 km office")
    km = sum(x["km"] for x in tr)
    print(f"{mo}: {len(tr)} trip(s), {km:g} km" + (f", claim {inr(km * d['rate'])} at {inr(d['rate'])}/km." if d["rate"] else ". Set a rate with:  mileage rate 8"))
