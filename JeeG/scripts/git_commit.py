# keywords: git commit, commit, save changes, commit all, commit message
# desc: Stage everything and commit (git commit fix login bug)
# category: developer
# usage: git commit <message>
# confirm: yes
# rawargs: yes
from _lib import args_text, call, fail
m = args_text()
if not m:
    fail("Usage: git commit <message>")
rc = call(["git", "add", "-A"])
raise SystemExit(rc or call(["git", "commit", "-m", m]))
