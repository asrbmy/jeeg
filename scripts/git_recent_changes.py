# keywords: git recent changes, git changes, what changed recently, recent commits, git whats new, changes this week, git activity, git history recent, latest changes
# desc: What changed in this git project recently (git recent changes, git recent changes 14 days)
# category: developer
# usage: git recent changes [days]
# rawargs: yes
import re, subprocess
from _lib import args_text, fail
m = re.search(r"(\d+)\s*(day|week|month)?", args_text())
days = int(m.group(1)) * ({"day": 1, "week": 7, "month": 30}.get(m.group(2) or "day", 1)) if m else 7
if not 1 <= days <= 3650: fail("Choose between 1 day and 10 years.")
r = subprocess.run(["git", "log", f"--since={days} days ago", "--stat", "--date=short", "--format=%n%h  %ad  %an  %s", "-n", "30"], capture_output=True, text=True, errors="replace")
if r.returncode: fail("This folder is not a git repository." if "not a git" in r.stderr else r.stderr.strip())
out = r.stdout.strip()
lines = out.splitlines()
print("\n".join(lines[:80]) if lines else f"No commits in the last {days} days.")
if len(lines) > 80: print(f"... ({len(lines) - 80} more lines; use a shorter period)")
