# keywords: git diff, diff, changes summary, what changed, uncommitted
# desc: Summarise uncommitted git changes
# category: developer
from _lib import call
raise SystemExit(call(['git', 'diff', '--stat']))
