# keywords: remember, jeeg remember, memory list, what do you remember, forget memory, my preferences memory, remember that
# desc: Tell JeeG facts or preferences to remember on this computer (remember I prefer metric units); the agent uses them. remember list | remember search <words> | remember forget <number|all>. Never keeps passwords.
# category: ai
# usage: remember <fact> [for 30 days] | remember review | remember list | remember search <words> | remember forget <number|all>
# rawargs: full
# patterns: ^\s*remember\b(?!\s+(?:the\s+|my\s+)?clipboard)
# priority: 9
import os, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import args_text, data_dir, fail
import jeeg_mind
t = re.sub(r"^\s*remember\s*(?:that\s+)?", "", args_text(), flags=re.I).strip()
m = jeeg_mind.Mind(data_dir())
low = t.lower()
if low in ("", "list", "all", "show"):
    mem = m.memories()
    if not mem: print("Nothing remembered yet. Try:  remember I prefer metric units")
    for x in mem: print(f"{x['id']:>3}. {x['text']}" + (f"   (until {time.strftime('%Y-%m-%d', time.localtime(x['expires']))}{', expired' if x['expires'] < time.time() else ''})" if x.get("expires") else ""))
elif low.startswith("search "):
    q = set(jeeg_mind.words(t[7:])); hits = [x for x in m.memories() if q & set(jeeg_mind.words(x["text"]))]
    for x in hits: print(f"{x['id']:>3}. {x['text']}")
    if not hits: print("No memory matches.")
elif low == "review":
    if os.environ.get("JEEG_VIA_AI"): fail("Only you can review memory.")
    sug = m.suggestions()
    if not sug: print("Nothing is waiting for your review.")
    if sug and not (sys.stdin and sys.stdin.isatty()):
        for x in sug: print(f"- {x['text']}   (from {x['source']})")
        fail("Run this in a terminal to keep or drop them.")
    while sug:
        x = sug[0]
        a = input(f"Keep this?  \"{x['text']}\"   (from {x['source']})  [y/N/q] ").strip().lower()
        if a == "q": break
        try: m.resolve_suggestion(0, a in ("y", "yes")); print("Kept." if a in ("y", "yes") else "Dropped.")
        except jeeg_mind.MindError as e: print(str(e))
        sug = m.suggestions()
elif low.startswith("forget"):
    if os.environ.get("JEEG_VIA_AI"): fail("Only you can change memory.")
    if t[6:].strip().lower() == "expired": print(f"Forgot {m.drop_expired()} expired."); raise SystemExit(0)
    try: n = m.forget(t[6:].strip())
    except jeeg_mind.MindError as e: fail(str(e))
    print(f"Forgot {n}.")
else:
    if os.environ.get("JEEG_VIA_AI"): fail("Only you can change memory.")
    days = 0
    dm = re.search(r"\s+for\s+(\d{1,4})\s+days?\s*$", t, re.I)
    if dm: days = int(dm.group(1)); t = t[: dm.start()].strip()
    kind = "preference" if re.match(r"(?i)i\s+(?:prefer|like|want|always|never|use)\b", t) else "fact"
    try: n = m.remember(t, kind, days)
    except jeeg_mind.MindError as e: fail(str(e))
    print(f"Remembered (#{n})" + (f", for {days} days." if days else "."))
