# keywords: git pull, pull, update repo, sync, latest changes, fetch latest
# desc: Pull the latest changes (fast-forward only)
# category: developer
from _lib import call
raise SystemExit(call(['git', 'pull', '--ff-only']))
