# keywords: install bundle, setup dev machine, setup new computer, new pc setup, install essentials, install pack, dev setup, office setup, install my tools
# desc: Install a set of apps in one go (install dev bundle: git, python, vscode, nodejs; also office, media, student, privacy). Add "preview" to see the commands only.
# category: system
# network: yes
# usage: install <dev|office|media|student|privacy> bundle [preview]
# confirm: yes
# rawargs: full
# patterns: ^\s*(?:install|setup|set\s+up)\s+(?:a\s+|my\s+|the\s+)?(?:dev|developer|office|media|student|privacy)\s+(?:bundle|pack|setup|tools|machine|computer|laptop|pc)\b ;; \b(?:new|fresh)\s+(?:computer|pc|laptop)\s+setup\b ;; ^\s*(?:install|setup|set\s+up)\s+(?:a\s+|my\s+|the\s+)?(?:\w+\s+)?bundle\b
# priority: 4
import re
from _apps import BUNDLES, is_preview, plan, execute
from _lib import args_text
t = args_text().lower()
name = next((k for k in BUNDLES if re.search(rf"\b{k}\b", t)), "dev" if re.search(r"\bdeveloper\b", t) else None)
if not name:
    print("Bundles:")
    for k, v in BUNDLES.items():
        print(f"  {k:<8} {', '.join(v)}")
    print("Say for example:  install dev bundle")
    raise SystemExit(0)
preview = is_preview(t)
print(f"Bundle '{name}': {', '.join(BUNDLES[name])}")
bad = 0
for app in BUNDLES[name]:
    p = plan("install", app)
    if "error" in p:
        print(f"  {app}: {p['error']}")
        bad += 1
        continue
    print(f"- {app}")
    if execute(p, preview):
        print(f"  {app}: did not finish (it may already be installed, or needs approval).")
        bad += 1
print("Preview only: nothing was changed." if preview else f"Finished. {len(BUNDLES[name]) - bad} of {len(BUNDLES[name])} worked.")
raise SystemExit(1 if bad and not preview else 0)
