# keywords: git clone, clone, download repo, clone repo, clone repository, copy repo
# desc: Clone a repository (git clone https://github.com/user/repo)
# category: developer
# usage: git clone <url>
import re
from _lib import args_text, call, fail
u = (args_text().split() or [""])[0]
if not re.fullmatch(r"(https://|git@|ssh://)[\w.@:/~\-]+?(\.git)?/?", u):
    fail("Usage: git clone <https or ssh repository URL>")
raise SystemExit(call(["git", "clone", u]))
