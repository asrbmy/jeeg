# keywords: 80c, tax saving, tax saving investments, section 80c, ppf elss, tax deduction
# desc: Track your Section 80C investments against the 1,50,000 limit (80c add 50000 ppf, 80c, 80c remove ppf)
# category: money
# usage: 80c add <amount> <what> | 80c | 80c remove <what>
# rawargs: full
# patterns: ^\s*(section\s+)?80\s*c\b
# priority: 4
import re
from _lib import args_text, fail
from _store import load, save
from _money import inr
LIMIT = 150000
t = re.sub(r"^\s*(?:section\s+)?80\s*c\s*", "", args_text(), flags=re.I).strip()
sub, _, body = t.partition(" "); sub, body = sub.lower(), body.strip()
d = load("tax80c.json", {})
if sub == "add":
    m = re.match(r"^(\d[\d,]*(?:\.\d{1,2})?)\s+(.+)$", body)
    if not m or not 0 < float(m.group(1).replace(",", "")) < 1e9: fail("Usage: 80c add <amount> <what>   e.g. 80c add 50000 ppf")
    k = m.group(2).lower()[:40]
    d[k] = d.get(k, 0) + float(m.group(1).replace(",", "")); save("tax80c.json", d); print(f"Saved {k}: {inr(d[k])}.")
elif sub in {"remove", "delete"}:
    if body.lower() not in d: fail("Say which one: " + (", ".join(d) or "(nothing saved yet)"))
    del d[body.lower()]; save("tax80c.json", d); print(f"Removed {body.lower()}.")
if sub not in {"add", "remove", "delete", ""} and sub != "":
    fail("Say: 80c add <amount> <what> | 80c | 80c remove <what>")
tot = sum(d.values())
if not d: fail("Nothing saved yet. Example:  80c add 50000 ppf")
for k, v in sorted(d.items(), key=lambda x: -x[1]): print(f"  {k:<24}{inr(v):>14}")
print(f"Total {inr(tot)} of {inr(LIMIT)}; " + (f"{inr(LIMIT - tot)} still to use." if tot < LIMIT else "the limit is reached (extra does not count). Limits can change; check the current rule."))
