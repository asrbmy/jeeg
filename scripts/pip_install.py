# keywords: pip, install, pip install, python package, install package, install library, install module
# desc: Install Python packages (pip install requests)
# category: developer
# usage: pip install <packages>
# confirm: yes
import re, subprocess, sys
from _lib import args_text, fail
pk = [p for p in args_text().replace(",", " ").split() if p.lower() not in ("package", "packages", "library", "module")]
bad = [p for p in pk if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._\-\[\],=<>!~]*", p)]
if not pk or bad:
    fail("Usage: pip install <package names>" + (f"   (invalid: {', '.join(bad)})" if bad else ""))
raise SystemExit(subprocess.call([sys.executable, "-m", "pip", "install", *pk]))
