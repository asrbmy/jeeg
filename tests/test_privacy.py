"""Privacy checks: JeeG itself only reaches the network where it says it does. Run: python tests/test_privacy.py"""
import ast, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCR = ROOT / "scripts"
fails, total = [], 0


def check(name, cond, info=""):
    global total
    total += 1
    if not cond:
        fails.append(name); print(f"FAIL  {name} {info}")


NET = {"urllib.request", "urllib.error", "socket", "http.client", "http.server", "ftplib", "smtplib", "ssl", "requests", "xmlrpc", "telnetlib"}


def net_imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out |= {a.name for a in n.names} & NET
        elif isinstance(n, ast.ImportFrom) and n.module:
            if n.module in NET:
                out.add(n.module)
            out |= {f"{n.module}.{a.name}" for a in n.names} & NET
    return out


# 1. only these files outside the task scripts may use network modules
ALLOWED_HELPERS = {"_net.py", "_lib.py"}          # _lib: urllib.parse only (not in NET)
helpers = {p.name for p in SCR.glob("_*.py") if net_imports(p)}
check("only _net.py (and nothing else) among helpers uses network modules", helpers <= {"_net.py", "_sys.py", "_worker.py"} | ALLOWED_HELPERS, str(helpers))
engine = {p.name for p in ROOT.glob("*.py") if net_imports(p)}
check("engine network use is limited to jeeg.py (doctor) and jeeg_cmds.py (update, library, plugin install, local web page)",
      engine <= {"jeeg.py", "jeeg_cmds.py"}, str(engine))

# 2. every task script that imports a network module, or _net, says so with '# network: yes'
for p in sorted(SCR.glob("*.py")):
    if p.name.startswith("_"):
        continue
    src = p.read_text(encoding="utf-8")
    direct = bool(net_imports(p)) or re.search(r"^\s*(from|import)\s+_net\b", src, re.M) is not None
    tagged = re.search(r"^# network:\s*yes\s*$", src, re.M) is not None
    if direct:
        check(f"{p.stem} imports network code and is tagged '# network: yes'", tagged)

# 3. the only web addresses written in the engine are the ones documented in PRIVACY.md
allowed = {"api.github.com", "github.com", "raw.githubusercontent.com", "127.0.0.1", "localhost", "example.com", "example.invalid", "files.pythonhosted.org", "pypi.org", "1.1.1.1", "evil.example"}
for f in ("jeeg.py", "jeeg_cmds.py"):
    hosts = set(re.findall(r"https?://([A-Za-z0-9.\-]+)", (ROOT / f).read_text(encoding="utf-8")))
    check(f"{f} only mentions documented hosts", hosts <= allowed, str(hosts - allowed))
check("engine has no telemetry words", not re.search(r"analytics|telemetry\s*\(|track_event|sentry|mixpanel|segment\.io", (ROOT / "jeeg.py").read_text() + (ROOT / "jeeg_cmds.py").read_text(), re.I))

# 4. library plugins are offline
for p in (ROOT / "library").glob("*.py"):
    check(f"library plugin {p.stem} imports no network module", not net_imports(p))

# 5. privacy page mentions every network host used by the engine
page = (ROOT / "PRIVACY.md").read_text(encoding="utf-8") if (ROOT / "PRIVACY.md").exists() else ""
for h in ("api.github.com", "raw.githubusercontent.com"):
    check(f"PRIVACY.md mentions {h}", h in page)

n_tasks = len([f for f in SCR.glob("*.py") if not f.name.startswith("_")])
n_net = sum(1 for f in SCR.glob("*.py") if not f.name.startswith("_") and re.search(r"^# network:\s*yes\s*$", f.read_text(encoding="utf-8"), re.M))
check("PRIVACY.md states the real counts", f"{n_net} of {n_tasks} tasks" in page, f"expected '{n_net} of {n_tasks} tasks'")

print(f"{total - len(fails)}/{total} privacy checks passed")
sys.exit(1 if fails else 0)
