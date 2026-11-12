# keywords: search app, find app, find software, find program, search package, what can i install, installable apps
# desc: Find an app in your package manager (search app video editor), or list the apps I can install by short name (search app)
# category: system
# network: yes
# usage: search app [words]
# rawargs: full
# patterns: ^\s*(?:search|find|look\s+for)\s+(?:an?\s+)?(?:app|apps|software|program|programs|package|packages)\b ;; \bwhat\s+(?:apps|software|programs)\s+can\s+(?:you|i)\s+install\b ;; ^\s*(?:list\s+)?installable\s+(?:apps|software)\b
# priority: 3
import re, subprocess
from _apps import BUNDLES, CATALOG, available, plan, split_names, SAFE_NAME
from _lib import args_text
t = re.sub(r"^\s*(?:search|find|look\s+for)?\s*(?:an?\s+)?(?:app|apps|software|programs?|packages?)?\s*(?:for)?\s*", "", args_text(), flags=re.I).strip()
t = re.sub(r"\b(what|can|you|i|install|list|installable)\b", " ", t, flags=re.I).strip()
if not t:
    print("Apps I can install by short name:")
    print("  " + ", ".join(sorted(CATALOG)))
    print("Bundles:  " + "; ".join(f"{k} = {', '.join(v)}" for k, v in BUNDLES.items()) + "     (say: install dev bundle)")
    print("Anything else:  search app <words>   then   install <exact name>")
    raise SystemExit(0)
if not SAFE_NAME.match(t):
    print("Use plain words to search (letters and numbers).")
    raise SystemExit(1)
hits = [k for k in CATALOG if t.lower() in k or any(t.lower() in a for a, c in __import__("_apps").ALIAS.items() if c == k)]
if hits:
    print("In my built-in list: " + ", ".join(sorted(hits)) + "   (say: install " + hits[0] + ")")
p = plan("search", t)
if "error" in p:
    print(p["error"])
    raise SystemExit(0 if hits else 1)
print(f"Searching with {p['manager']} ...")
try:
    r = subprocess.run(p["cmd"], capture_output=True, text=True, errors="replace", timeout=60, stdin=subprocess.DEVNULL)
    lines = [l for l in (r.stdout or "").splitlines() if l.strip()]
    print("\n".join(lines[:25]) if lines else "Nothing found.")
    if len(lines) > 25:
        print(f"... {len(lines) - 25} more lines. Add more words to narrow it down.")
except (OSError, subprocess.SubprocessError):
    print("The search could not run (offline, or the package manager is busy).")
