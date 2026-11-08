"""Quality gates: every task is well formed, compiles, is documented, and JeeG stays small and quick."""
import os, re, subprocess, sys, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
home = tempfile.mkdtemp(prefix="jeeg-quality-")
os.environ["JEEG_HOME"] = home
import jeeg

P = F = 0
def ok(c, label):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", label)

SCR = ROOT / "scripts"
tasks = sorted(p for p in SCR.glob("*.py") if not p.name.startswith("_"))
ents = {e["name"]: e for e in jeeg.load_index(jeeg.script_dirs([]))}
ok(len(tasks) == len(ents), f"every script is indexed ({len(tasks)} files, {len(ents)} tasks)")
CATS = {e["cat"] for e in ents.values()}
ok(len(CATS) <= 60, f"categories stay manageable ({len(CATS)})")
for p in tasks:
    n = p.stem
    e = ents.get(n)
    ok(re.fullmatch(r"[a-z][a-z0-9_]*", n) is not None, f"{n}: name is lowercase letters, digits, _")
    ok(e is not None and len(e["desc"]) >= 8, f"{n}: has a description")
    ok(e is not None and e["cat"] != "general", f"{n}: has a category")
    ok(p.stat().st_size < 40_000, f"{n}: under 40 KB")
    src = p.read_text(encoding="utf-8")
    try:
        compile(src, str(p), "exec")
    except SyntaxError as ex:
        ok(False, f"{n}: does not compile: {ex}")
    ok("\t" not in src.split("\n", 12)[0] and not re.search(r"\bpassword\s*=\s*['\"][^'\"]+['\"]", src), f"{n}: no hard-coded secrets")
    ok(not re.search(r"os\.system\(|shell\s*=\s*True", src), f"{n}: no shell=True / os.system")

# code that only works on newer Pythons than 3.9 (CI runs 3.9 and 3.12, but a developer may only test on one)
NEWER = [(re.compile(r"\.(?:write|read)_text\([^)]*newline="), "Path.write_text(newline=) needs Python 3.10"),
         (re.compile(r"\bmatch\s+[\w.()]+\s*:\s*$", re.M), "match statement needs Python 3.10"),
         (re.compile(r"\bzip\([^)]*strict="), "zip(strict=) needs Python 3.10"),
         (re.compile(r"\.bit_count\(|datetime\.UTC\b|import tomllib"), "needs Python 3.10 or 3.11")]
for p in list(ROOT.glob("*.py")) + list(SCR.glob("*.py")) + list((ROOT / "library").glob("*.py")) + list((ROOT / "tools").glob("*.py")):
    src = p.read_text(encoding="utf-8")
    try:
        compile(src, str(p), "exec")        # on Python 3.9 this also catches newer syntax such as same-quote f-strings
    except SyntaxError as ex:
        ok(False, f"{p.name}: does not compile on this Python: {ex}")
    for rx, why in NEWER:
        ok(not rx.search(src), f"{p.name}: {why}")

# every phrase in the routing list points at a task that exists
for ln in (ROOT / "tests" / "phrases.txt").read_text(encoding="utf-8").splitlines():
    m = re.match(r"^.*?=>\s*([a-z0-9_]+)\s*\|", ln)
    if m:
        ok(m.group(1) in ents or m.group(1) == "none", f"phrases.txt names a real task: {m.group(1)}")

# size and speed budgets
size = sum(p.stat().st_size for p in list(ROOT.glob("*.py")) + list(SCR.glob("*.py")))
ok(size < 3_000_000, f"code stays small ({size // 1024} KB, limit 3000 KB)")
env = dict(os.environ, JEEG_HOME=home)
t = time.perf_counter(); subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "--version"], env=env, capture_output=True); v = time.perf_counter() - t
ok(v < 1.5, f"--version in {v:.2f}s (limit 1.5s)")
idx = Path(home) / "index.json"
if idx.exists(): idx.unlink()
t = time.perf_counter(); subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "gst", "100", "5"], env=env, capture_output=True); cold = time.perf_counter() - t
t = time.perf_counter(); subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "gst", "100", "5"], env=env, capture_output=True); warm = time.perf_counter() - t
ok(cold < 6.0, f"first run (index build) {cold:.2f}s (limit 6s)")
ok(warm < 1.5, f"normal run {warm:.2f}s (limit 1.5s)")
import jeeg_api
t = time.perf_counter(); jeeg_api.find("open youtube"); f1 = time.perf_counter() - t
ok(f1 < 1.0, f"matching a phrase takes {f1:.2f}s (limit 1s)")

print(f"quality checks: {P} passed, {F} failed")
sys.exit(1 if F else 0)
