# keywords: routine, run routine, my routine, custom routine, macro, workflow
# desc: Run any routine from your routines file (run routine <name> [words]; steps can use {1} {2} {args})
# category: routines
# usage: run routine <name> [words]
# rawargs: full
# patterns: ^\s*(please\s+)?(run|start|do|play|launch)\s+(my\s+)?routine\b
# priority: 1
import re
from _lib import args_text, fail
from _routine import run, load
t = re.sub(r"^\s*(?:(?:please|can|you|run|start|do|play|launch|my)\s+)*routines?\s*", "", args_text(), flags=re.I).split()
if not t:
    fail("Usage: run routine <name> [words]   (see: list routines)")
known = load()
low = [w.lower() for w in t]
for n in range(len(t), 0, -1):                 # longest name first; the rest are the routine's own words
    key = "_".join(low[:n])
    if key in known:
        run(key, t[n:])
        break
else:
    run("_".join(low))                          # prints the 'no such routine' message
