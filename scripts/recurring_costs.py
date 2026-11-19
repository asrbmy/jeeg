# keywords: recurring, subscription, monthly cost, recurring expense, netflix monthly, rent monthly, subscriptions
# desc: Costs that repeat every month (recurring add 649 netflix entertainment, recurring list, recurring apply, recurring remove netflix)
# category: money
# usage: recurring add <amount> <name> [category] | recurring list | recurring apply | recurring remove <name>
# rawargs: full
# patterns: ^\s*recurring\s+(add|list|apply|remove|delete|costs?|payments?|expenses?)\b
# priority: 4
import csv, datetime, re
from _lib import args_text, data_dir, fail
from _store import load, save
from _money import inr
t = re.sub(r"^\s*recurring\s*", "", args_text(), flags=re.I).strip()
sub, _, body = t.partition(" ")
sub, body = sub.lower(), body.strip()
items = load("recurring.json", [])
if sub == "add":
    m = re.match(r"^(\d[\d,]*(?:\.\d{1,2})?)\s+(.+)$", body)
    if not m:
        fail("Usage: recurring add <amount> <name> [category]   e.g. recurring add 649 netflix entertainment")
    amt = float(m.group(1).replace(",", ""))
    if not 0 < amt < 1e9:
        fail("Amount must be positive.")
    words = m.group(2).lower().split()
    name, cat = words[0], (words[1] if len(words) > 1 else "subscriptions")
    if len(items) >= 100 and not any(i["name"] == name for i in items):
        fail("That is a lot of recurring costs; remove some first.")
    items = [i for i in items if i["name"] != name]
    items.append({"name": name, "amount": amt, "category": cat, "last": ""})
    save("recurring.json", items)
    print(f"Saved {name}: {inr(amt)} every month under '{cat}'. Add this month's costs with:  recurring apply")
elif sub in {"remove", "delete"}:
    n = body.lower()
    keep = [i for i in items if i["name"] != n]
    if len(keep) == len(items):
        fail("Say which one: " + (", ".join(i["name"] for i in items) or "(nothing saved yet)"))
    save("recurring.json", keep)
    print(f"Removed {n}.")
elif sub == "apply":
    mo = datetime.date.today().strftime("%Y-%m")
    todo = [i for i in items if i.get("last") != mo]
    if not todo:
        print(f"Everything is already added for {mo}." if items else "Nothing saved yet. Example:  recurring add 649 netflix")
        raise SystemExit(0)
    f = data_dir() / "expenses.csv"
    new = not f.exists()
    with open(f, "a", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        if new:
            wr.writerow(["date", "amount", "category", "note"])
        for i in todo:
            wr.writerow([datetime.date.today().isoformat(), f"{i['amount']:.2f}", i["category"], i["name"] + " (recurring)"])
            i["last"] = mo
    save("recurring.json", items)
    print(f"Added {len(todo)} cost(s) for {mo}, total {inr(sum(i['amount'] for i in todo))}.")
else:
    if not items:
        fail("Nothing saved yet. Example:  recurring add 649 netflix entertainment")
    print("Recurring costs:")
    for i in sorted(items, key=lambda x: -x["amount"]):
        print(f"  {i['name']:<18}{inr(i['amount']):>14}  {i['category']}" + ("" if i.get("last") else "  (not added yet)"))
    tot = sum(i["amount"] for i in items)
    print(f"  Total per month {inr(tot)}; per year {inr(tot * 12)}.")
