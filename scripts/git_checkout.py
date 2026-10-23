# keywords: git checkout, switch branch, change branch, git switch, go to branch, new branch, create branch, checkout branch
# desc: Switch to a git branch, or create one (git switch main, git checkout new feature-x)
# category: developer
# usage: git checkout <branch> | git checkout new <branch>
# rawargs: yes
import re, subprocess
from _lib import args_text, call, fail
t = re.sub(r"\b(to|branch|the|onto|switch|checkout|change|go|goto|git)\b", " ", args_text(), flags=re.I).split()
create = bool(t) and t[0].lower() in ("new", "create", "-b")
if create: t = t[1:]
if len(t) != 1: fail("Usage: git checkout <branch>     or    git checkout new <branch>")
b = t[0]
if b.startswith("-") or subprocess.run(["git", "check-ref-format", "--branch", b], capture_output=True).returncode: fail(f"'{b}' is not a valid branch name.")
raise SystemExit(call(["git", "switch", "-c", b] if create else ["git", "switch", b]))
