# keywords: git log, commits, history, recent commits, commit history, last commits
# desc: Show the last 10 git commits
# category: developer
from _lib import call
raise SystemExit(call(['git', 'log', '-10', '--oneline', '--graph', '--decorate']))
