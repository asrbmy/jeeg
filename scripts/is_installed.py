# keywords: is it installed, installed or not, do i have
# desc: Check whether a program is installed and which version (is git installed, which version of python, do i have vlc)
# category: system
# usage: is <app> installed | version of <app>
# rawargs: full
# patterns: \bis\s+(?:the\s+)?[\w\.\+\- ]{1,30}?\s+installed\b ;; \b(?:do\s+i\s+have|have\s+i\s+got)\s+[\w\.\+\-]+\b ;; \b(?:which|what)\s+version\s+of\s+[\w\.\+\-]+(?:\s+do\s+i\s+have|\s+is\s+installed)?\s*$ ;; \bversion\s+of\s+[\w\.\+\-]+\s*(?:installed)?\s*$
# priority: 4
import os, re, shutil, subprocess
from _apps import lookup, split_names
from _lib import MAC, WIN, args_text, fail

t = args_text().lower()
t = re.sub(r"\b(?:is|are|do|i|have|got|which|what|version|of|installed|check|if|on|my|computer|pc|the|here|already|and|its|it|a|an)\b", " ", t)
names = split_names(t)
if not names:
    fail("Say which program, for example:  is git installed")
COMMANDS = {"vscode": ["code"], "nodejs": ["node"], "python": ["python3", "python"], "chrome": ["google-chrome", "chrome", "chromium"],
            "7zip": ["7z", "7za"], "golang": ["go"], "go": ["go"], "rust": ["rustc"], "docker desktop": ["docker"], "java": ["java"], "node": ["node"],
            "vs code": ["code"], "visual studio code": ["code"]}


def first_line(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=8, errors="replace", stdin=subprocess.DEVNULL)
        for ln in ((r.stdout or "") + (r.stderr or "")).splitlines():
            if ln.strip():
                return ln.strip()[:100]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""


def find(name):
    key, _ = lookup(name)
    cands = COMMANDS.get(name) or COMMANDS.get(key or "") or []
    for c in cands + [(key or name).split()[0], name.replace(" ", "-"), name.split()[0]]:
        if re.fullmatch(r"[A-Za-z0-9._+\-]+", c or "") and shutil.which(c):
            return shutil.which(c), c
    if MAC:
        for nm in {name.title(), (key or name).title()}:
            for base in ("/Applications", os.path.expanduser("~/Applications")):
                if os.path.isdir(f"{base}/{nm}.app"):
                    return f"{base}/{nm}.app", None
    if not WIN and not MAC and shutil.which("dpkg"):
        try:
            pkg = (key or name).replace(" ", "-")
            if re.fullmatch(r"[a-z0-9.+\-]+", pkg) and subprocess.run(["dpkg", "-s", pkg], capture_output=True, timeout=8).returncode == 0:
                return f"package {pkg}", None
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None, None


code = 0
for n in names:
    where, cmd = find(n)
    if not where:
        print(f"{n}: not found.  Install it with:  install {n}")
        code = 1
        continue
    ver = first_line([cmd, "--version"]) if cmd and lookup(n)[0] else ""      # only programs in the built-in list are run, never an arbitrary name
    print(f"{n}: installed ({where})" + (f"\n    {ver}" if ver else ""))
raise SystemExit(code)
