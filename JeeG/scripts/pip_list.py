# keywords: pip list, installed packages, python packages, installed libraries, which packages, pip freeze
# desc: List installed Python packages
# category: developer
import subprocess, sys
raise SystemExit(subprocess.call([sys.executable, '-m', 'pip', 'list']))
