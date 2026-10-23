# keywords: git, status, git status, changes, repo status, modified, what changed
# desc: Show git status of the current folder
# category: developer
from _lib import call
raise SystemExit(call(['git', 'status', '-sb']))
