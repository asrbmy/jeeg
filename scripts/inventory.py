# keywords: inventory, stock count, shop stock, low stock, stock add, stock remove, items in stock, godown, store stock
# desc: Keep a simple stock list for a shop or home (stock add rice 20 min 5, stock sell rice 3, stock list, low stock)
# category: money
# usage: stock add <item> <qty> [min <n>] | stock sell|remove <item> <qty> | stock set <item> <qty> | stock list | low stock | stock delete <item>
# rawargs: full
# patterns: ^\s*(?:stock|inventory)\s+(?:add|sell|sold|remove|use|set|delete|list|show|count)\b ;; \blow\s+(?:on\s+)?(?:stock|inventory)\b ;; \b(?:what|which)\s+(?:items\s+)?(?:is|are)\s+(?:running\s+)?(?:low|out\s+of\s+stock)\b
# priority: 4
import re
from _lib import args_text, fail
from _store import load, save

text = args_text().strip()
low = text.lower()
inv = load("inventory.json", {})
ITEM = r"[a-z0-9][a-z0-9 _\-\.]{0,39}?"
NUM = r"\d+(?:\.\d+)?"


def fmt(n):
    return f"{n:g}"


def show(items):
    if not items:
        print("(nothing)")
    for k in sorted(items):
        v = items[k]
        flag = "   <-- LOW" if v["qty"] <= v["min"] and v["min"] > 0 else ""
        print(f"  {k:<28} {fmt(v['qty']):>8}   min {fmt(v['min'])}{flag}")


if re.search(r"\blow\b|out\s+of\s+stock", low) and not re.match(r"^(stock|inventory)\s+(add|set|sell|sold|remove|use)\b", low):
    lows = {k: v for k, v in inv.items() if v["min"] > 0 and v["qty"] <= v["min"]}
    if not lows:
        print("Nothing is low." if inv else "No stock yet. Add some:  stock add rice 20 min 5")
    else:
        print(f"{len(lows)} item(s) to buy:")
        show(lows)
    raise SystemExit(0)
if re.match(r"^(?:stock|inventory)\s+(?:list|show|count)\s*$", low) or low in {"stock", "inventory"}:
    if not inv:
        fail("No stock yet. Add some:  stock add rice 20 min 5")
    print(f"{len(inv)} item(s):")
    show(inv)
    raise SystemExit(0)
m = re.match(rf"^(?:stock|inventory)\s+add\s+({ITEM})\s+({NUM})(?:\s+(?:min|minimum|low)\s+({NUM}))?\s*$", low)
if m:
    k, q = m.group(1).strip(), float(m.group(2))
    cur = inv.setdefault(k, {"qty": 0.0, "min": 0.0})
    cur["qty"] += q
    if m.group(3) is not None:
        cur["min"] = float(m.group(3))
    if len(inv) > 5000:
        fail("That is too many items.")
    save("inventory.json", inv)
    print(f"{k}: {fmt(cur['qty'])} in stock" + (f" (warn at {fmt(cur['min'])})" if cur["min"] else ""))
    raise SystemExit(0)
m = re.match(rf"^(?:stock|inventory)\s+(sell|sold|remove|use)\s+({ITEM})\s+({NUM})\s*$", low)
if m:
    k, q = m.group(2).strip(), float(m.group(3))
    if k not in inv:
        fail(f"No item '{k}'. See:  stock list")
    cur = inv[k]
    if q > cur["qty"] + 1e-9:
        fail(f"Only {fmt(cur['qty'])} of {k} in stock; cannot take {fmt(q)}.")
    cur["qty"] = max(0.0, cur["qty"] - q)
    save("inventory.json", inv)
    print(f"{k}: {fmt(cur['qty'])} left" + ("   <-- LOW, time to buy more" if cur["min"] and cur["qty"] <= cur["min"] else ""))
    raise SystemExit(0)
m = re.match(rf"^(?:stock|inventory)\s+set\s+({ITEM})\s+({NUM})(?:\s+(?:min|minimum|low)\s+({NUM}))?\s*$", low)
if m:
    k = m.group(1).strip()
    cur = inv.setdefault(k, {"qty": 0.0, "min": 0.0})
    cur["qty"] = float(m.group(2))
    if m.group(3) is not None:
        cur["min"] = float(m.group(3))
    save("inventory.json", inv)
    print(f"{k}: set to {fmt(cur['qty'])}")
    raise SystemExit(0)
m = re.match(rf"^(?:stock|inventory)\s+delete\s+({ITEM})\s*$", low)
if m:
    k = m.group(1).strip()
    if k not in inv:
        fail(f"No item '{k}'.")
    del inv[k]
    save("inventory.json", inv)
    print(f"Removed {k}.")
    raise SystemExit(0)
fail("Try:  stock add rice 20 min 5   |   stock sell rice 3   |   stock list   |   low stock")
