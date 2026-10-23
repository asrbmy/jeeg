# keywords: git stash, stash changes, stash pop, stash list, save changes temporarily, shelve changes, put changes aside, restore stash
# desc: Stash or restore uncommitted changes (git stash, git stash pop, git stash list)
# category: developer
# usage: git stash [pop|list|save <note>]
# rawargs: yes
import re
from _lib import args_text, call, fail
t = args_text().lower().strip()
if t in ("", "save", "push", "changes"): cmd = ["git", "stash", "push"]
elif re.fullmatch(r"(pop|apply|restore|back|get back|restore changes)", t): cmd = ["git", "stash", "pop"]
elif re.fullmatch(r"(list|show|all)", t): cmd = ["git", "stash", "list"]
elif t.startswith(("save ", "push ", "message ")):
    msg = t.split(" ", 1)[1].strip()
    cmd = ["git", "stash", "push", "-m", msg]
else: fail("Usage: git stash | git stash pop | git stash list | git stash save <note>")
raise SystemExit(call(cmd))
