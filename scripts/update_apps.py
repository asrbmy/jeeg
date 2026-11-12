# keywords: update apps, upgrade apps, update all apps, upgrade all software, update software, update programs, update installed apps, outdated apps
# desc: Update all your installed apps (update all apps), or one (update app vlc); add "preview" to see the command only
# category: system
# network: yes
# usage: update all apps | update app <name> [preview]
# confirm: yes
# rawargs: full
# patterns: ^\s*(?:update|upgrade)\s+(?:all\s+|my\s+|the\s+|installed\s+)*(?:apps?|applications|software|programs?)\b ;; ^\s*(?:update|upgrade)\s+(?:everything|all)\s*(?:on\s+(?:my\s+)?(?:computer|pc|laptop))?\s*$ ;; ^\s*(?:update|upgrade)\s+app\s+\S
# priority: 3
import re
from _apps import available, execute, is_preview, os_name, run_action, with_sudo, split_names
from _lib import args_text, fail
import subprocess, sys
t = args_text()
preview = is_preview(t)
tl = re.sub(r"\b(update|upgrade|apps?|applications|software|programs?|my|the|installed|all|everything|on|computer|pc|laptop|preview|dry-run|dryrun|please)\b", " ", t.lower()).strip()
one = re.search(r"\bapp\s+\S", t.lower()) or (tl and not re.search(r"\b(all|everything)\b", t.lower()))
if one and split_names(t):
    raise SystemExit(run_action("upgrade", t))
mgrs = available()
if not mgrs:
    fail("No package manager found (Windows: winget or choco, Mac: brew, Linux: apt, dnf, pacman or flatpak).")
cmds = []
for m in mgrs:
    cmds += {"winget": [["winget", "upgrade", "--all"]], "choco": [["choco", "upgrade", "all", "-y"]], "brew": [["brew", "update"], ["brew", "upgrade"]],
             "apt-get": [["apt-get", "update"], ["apt-get", "upgrade", "-y"]], "dnf": [["dnf", "upgrade", "-y"]],
             "pacman": [["pacman", "-Syu", "--noconfirm"]], "flatpak": [["flatpak", "update", "-y"]]}[m]
code = 0
for c in cmds:
    p = {"cmd": c, "sudo": c[0] in {"apt-get", "dnf", "pacman"}}
    rc = execute(p, preview)
    if rc:
        print(f"{c[0]} reported an error (code {rc}).")
        code = 1
print("Preview only: nothing was changed." if preview else ("Finished with errors." if code else "All done."))
raise SystemExit(code)
