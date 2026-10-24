# keywords: medicine today, medicine taken, took medicine, medicine remind, remove medicine, medicine list, which medicine, pills today
# desc: Today's medicine list; tick one off, or get alerts for the rest of today (medicine today, medicine taken metformin, medicine remind, remove medicine metformin)
# category: health
# usage: medicine today | medicine taken <name> | medicine remind | remove medicine <name>
# rawargs: yes
# private: yes
# patterns: \bmedicine\s+(today|taken|remind|list)\b ;; \b(took|taken)\s+(my\s+)?(medicine|pill|tablet)\b ;; \bremove\s+medicine\b ;; \b(which|what)\s+(medicine|pills|tablets)\b
# priority: 2
import datetime, re, time
from _lib import args_text, fail
from _store import load, save
t = args_text().lower()
med = load("medicines.json", {})
if not med:
    fail("No medicines saved. Example:  add medicine metformin at 8am and 8pm")
today = datetime.date.today().isoformat()
now = datetime.datetime.now().strftime("%H:%M")
words = [w for w in re.findall(r"[a-z0-9 ]+", t)]
rm = re.search(r"\b(?:remove|delete|stop)\s+(?:medicine\s+)?(.+)$", t)
if rm:
    n = rm.group(1).replace("medicine", "").strip()
    if n not in med: fail(f"No medicine called '{n}'. You have: {', '.join(med)}")
    del med[n]; save("medicines.json", med); print(f"Removed {n}."); raise SystemExit(0)
tk = re.search(r"\b(?:taken|took|had|done)\s+(?:my\s+)?(.+)$", t)
if tk:
    n = re.sub(r"\b(medicine|today|my)\b", "", tk.group(1)).strip()
    hit = [k for k in med if n and (n == k or n in k or k in n)]
    if len(hit) != 1: fail(f"Say which one: {', '.join(med)}")
    k = hit[0]; done = med[k]["taken"].setdefault(today, [])
    due = [x for x in med[k]["times"] if x not in done and x <= now] or [x for x in med[k]["times"] if x not in done]
    if not due: print(f"All of today's {k} doses are already ticked."); raise SystemExit(0)
    done.append(due[0]); med[k]["taken"] = {d: v for d, v in med[k]["taken"].items() if d >= (datetime.date.today() - datetime.timedelta(days=30)).isoformat()}
    save("medicines.json", med); print(f"Ticked {k} for {due[0]}."); raise SystemExit(0)
if re.search(r"\bremind|alert|notify\b", t):
    from _time import start_worker
    n = 0
    for k, v in med.items():
        for x in v["times"]:
            if x in v["taken"].get(today, []) or x <= now: continue
            hh, mm = map(int, x.split(":"))
            when = datetime.datetime.combine(datetime.date.today(), datetime.time(hh, mm)).timestamp()
            start_worker("once", when, f"Take {k}", f"{x}: take {k}"); n += 1
    print(f"Set {n} reminder(s) for the rest of today." if n else "Nothing left to remind today.")
    print("They run in the background and stop at the end of the day. Put 'medicine remind' in your morning routine to get them every day.")
    raise SystemExit(0)
print(f"Medicines for {datetime.date.today():%A %d %B}:")
for k, v in sorted(med.items()):
    done = v["taken"].get(today, [])
    print(f"  {k}")
    for x in v["times"]:
        mark = "[x]" if x in done else ("[ ] (missed?)" if x < now else "[ ]")
        print(f"     {x}  {mark}")
