# keywords: git branch, branches, which branch, current branch, list branches
# desc: List git branches
# category: developer
from _lib import call
raise SystemExit(call(['git', 'branch', '-vv']))
