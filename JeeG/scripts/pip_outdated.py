# keywords: outdated, pip outdated, updates, upgradable, old packages, packages to update
# desc: List Python packages that have updates
# category: developer
import subprocess, sys
raise SystemExit(subprocess.call([sys.executable, '-m', 'pip', 'list', '--outdated']))
