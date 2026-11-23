# keywords: remember, jeeg remember, memory list, what do you remember, forget memory, my preferences memory, remember that
# desc: Tell JeeG facts or preferences to remember on this computer (remember I prefer metric units); the agent uses them. remember list | remember search <words> | remember forget <number|all>. Never keeps passwords.
# category: ai
# usage: remember <fact> | remember list | remember search <words> | remember forget <number|all>
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
    for x in mem: print(f"{x['id']:>3}. {x['text']}")
elif low.startswith("search "):
    q = set(jeeg_mind.words(t[7:])); hits = [x for x in m.memories() if q & set(jeeg_mind.words(x["text"]))]
    for x in hits: print(f"{x['id']:>3}. {x['text']}")
    if not hits: print("No memory matches.")
elif low.startswith("forget"):
    if os.environ.get("JEEG_VIA_AI"): fail("Only you can change memory.")
    try: n = m.forget(t[6:].strip())
    except jeeg_mind.MindError as e: fail(str(e))
    print(f"Forgot {n}.")
else:
    if os.environ.get("JEEG_VIA_AI"): fail("Only you can change memory.")
    kind = "preference" if re.match(r"(?i)i\s+(?:prefer|like|want|always|never|use)\b", t) else "fact"
    try: n = m.remember(t, kind)
    except jeeg_mind.MindError as e: fail(str(e))
    print(f"Remembered (#{n}).")
