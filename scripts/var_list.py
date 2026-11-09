# keywords: vars, variables, show vars, list variables, my variables, show my variables
# desc: Show your saved variables (vars, show variables).
# category: utility
# usage: vars
# patterns: ^\s*(show\s+|list\s+|my\s+)?(vars|variables)\s*$ ;; ^\s*(show|list)\s+my\s+(vars|variables)\s*$
# priority: 2
from _lib import var_all
vs = var_all()
if not vs:
    print("No variables yet. Try:  set var rate = 18   then   gst 1000 $rate")
else:
    for k in sorted(vs):
        print(f"  ${k:<14} = {vs[k]}")
    print(f"{len(vs)} variable(s). Use them as $name in any phrase; remove one with: remove var <name>")
