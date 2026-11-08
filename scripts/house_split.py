# keywords: flatmates, flat split, roommate expenses, house split, who owes whom, housemates
# desc: Share house costs between flatmates and see who pays whom (flat members amit ravi sam; flat add rent 18000 paid by amit; flat summary)
# category: money
# usage: flat members <names> | flat add <what> <amount> paid by <name> [split <names>] | flat summary | flat clear
# rawargs: full
# private: yes
# patterns: \b(flat|house)\s*(mates?)?\s+(members|add|summary|split|clear|expenses?)\b ;; \b(flatmates?|roommates?|housemates?)\b ;; \bwho\s+owes\s+whom\b ;; \bsplit\s+(the\s+)?rent\b
# priority: 3
import re
from _lib import args_text, fail
from _store import load, save
t = args_text().strip()
t = re.sub(r"^(?:house|flat|flatmates?|roommates?|housemates?)\s*(?:split|expenses?|costs?)?\s*", "", t, flags=re.I).strip()
data = load("house_split.json", {"members": [], "items": []})
low = t.lower()
if low.startswith("members") or low.startswith("people") or low.startswith("set"):
    names = [x.lower() for x in re.split(r"[\s,]+", re.sub(r"^(members|people|set)\s*", "", t, flags=re.I)) if x and x.lower() not in {"and", "are", "is"}]
    if len(set(names)) < 2 or len(names) > 20 or not all(re.fullmatch(r"[a-z][a-z0-9_.-]{0,19}", n) for n in names):
        fail("Usage: flat members amit ravi sam   (2 to 20 names, one word each)")
    data["members"] = sorted(set(names))
    save("house_split.json", data)
    print("Flatmates: " + ", ".join(n.title() for n in data["members"]))
    raise SystemExit(0)
if low.startswith("clear") or low.startswith("reset") or low.startswith("settled"):
    data["items"] = []
    save("house_split.json", data)
    print("Cleared all expenses (members kept).")
    raise SystemExit(0)
if low.startswith("add") or re.match(r"^[a-z ]+\s+\d", low) and not low.startswith(("summary", "show")):
    body = re.sub(r"^add\s+", "", t, flags=re.I)
    m = re.match(r"^(.+?)\s+(\d+(?:\.\d+)?)\s*(?:paid\s+by|by|from)\s+([a-z][\w.-]*)(?:\s+(?:split|between|for|among)\s+(.+))?$", body, re.I)
    if not m:
        fail("Usage: flat add rent 18000 paid by amit      (everyone shares)\n       flat add groceries 900 paid by ravi split ravi sam   (only some share)")
    if not data["members"]:
        fail("Set the flatmates first:  flat members amit ravi sam")
    what, amt, payer = m.group(1).strip()[:40], float(m.group(2)), m.group(3).lower()
    share = [x.lower() for x in re.split(r"[\s,]+", m.group(4)) if x and x.lower() not in {"and"}] if m.group(4) else data["members"]
    bad = [x for x in [payer] + share if x not in data["members"]]
    if bad or not 0 < amt < 1e9:
        fail("Unknown person: " + ", ".join(bad) + f".  Members: {', '.join(data['members'])}" if bad else "Check the amount.")
    data["items"].append({"what": what, "amt": amt, "payer": payer, "share": share})
    save("house_split.json", data)
    print(f"Added {what}: {amt:,.2f} paid by {payer.title()}, shared by {len(share)}.")
    raise SystemExit(0)
if not data["members"]:
    fail("Set the flatmates first:  flat members amit ravi sam")
if not data["items"]:
    fail("No expenses yet. Add one:  flat add rent 18000 paid by amit")
bal = {n: 0.0 for n in data["members"]}
for it in data["items"]:
    bal[it["payer"]] += it["amt"]
    for n in it["share"]:
        bal[n] -= it["amt"] / len(it["share"])
print(f"{len(data['items'])} expense(s), total {sum(i['amt'] for i in data['items']):,.2f}")
for it in data["items"][-8:]:
    print(f"  {it['what']:<18} {it['amt']:>10,.2f}  paid by {it['payer'].title()}")
debt = sorted([[n, -v] for n, v in bal.items() if v < -0.005], key=lambda x: -x[1])
cred = sorted([[n, v] for n, v in bal.items() if v > 0.005], key=lambda x: -x[1])
print("To settle up:")
if not debt:
    print("  Everyone is even.")
i = j = 0
while i < len(debt) and j < len(cred):
    pay = min(debt[i][1], cred[j][1])
    print(f"  {debt[i][0].title()} pays {cred[j][0].title()}  {pay:,.2f}")
    debt[i][1] -= pay; cred[j][1] -= pay
    if debt[i][1] < 0.005: i += 1
    if cred[j][1] < 0.005: j += 1
print("When everyone has paid, say:  flat clear")
