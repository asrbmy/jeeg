"""Security and robustness regression tests. Run: python tests/test_security.py (uses temporary folders)."""
import io, json, os, subprocess, sys, tarfile, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCR = ROOT / "scripts"
sys.path.insert(0, str(SCR))
fails, total = [], 0


def check(name, cond, info=""):
    global total
    total += 1
    if not cond:
        fails.append(name); print(f"FAIL  {name} {info}")


home = tempfile.mkdtemp()
jh = Path(home) / "jeeg"
env = dict(os.environ, HOME=home, USERPROFILE=home, JEEG_HOME=str(jh), PYTHONIOENCODING="utf-8", BROWSER="/bin/true")
os.environ.update(JEEG_HOME=str(jh))


def task(*a, timeout=60):
    return subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "-y", *a], capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL, timeout=timeout)


def script(name, *a):
    return subprocess.run([sys.executable, str(SCR / (name + ".py")), *a], capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL, timeout=60)


# ---- links: only safe schemes may be opened
import _lib
for bad in ("file:///etc/passwd", "javascript:alert(1)", "C:\\Windows\\System32\\calc.exe", "calc.exe", "ms-msdt:/id x", "https://a.com/\nfile:///x", "data:text/html,hi"):
    try:
        _lib.open_url(bad); check(f"open_url refuses {bad[:25]!r}", False)
    except SystemExit:
        check(f"open_url refuses {bad[:25]!r}", True)
import webbrowser
seen = []
webbrowser.open = lambda u: seen.append(u) or True
_lib.open_url("https://example.com/x?y=1"); _lib.open_url("mailto:a@b.com")
check("open_url allows https and mailto", seen == ["https://example.com/x?y=1", "mailto:a@b.com"], seen)

# a saved link that was hand-edited to something dangerous is refused
jh.mkdir(exist_ok=True)
(jh / "links.json").write_text(json.dumps({"evil": "file:///etc/passwd"}))
r = task("open link evil")
check("open link refuses a tampered link", "Refusing" in r.stdout and r.returncode != 0, r.stdout)

# ---- network helpers refuse other schemes
import _net
check("_net.get ignores file://", _net.get("file:///etc/passwd") is None)
r = script("http_get", "file:///etc/passwd")
check("http get refuses file://", "root:" not in r.stdout and r.returncode != 0, r.stdout)
r = script("http_get", "https://a.com/x y")
check("http get refuses spaces", r.returncode != 0)

# ---- private data folder
if os.name == "posix":
    d = Path(home) / "fresh"
    r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "-y", "todo add test"], env=dict(env, JEEG_HOME=str(d)), capture_output=True, text=True, stdin=subprocess.DEVNULL)
    check("data folder is private (700)", d.is_dir() and (d.stat().st_mode & 0o077) == 0, oct(d.stat().st_mode) if d.exists() else "missing")
    d2 = Path(home) / "open"; d2.mkdir(); d2.chmod(0o755)
    subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "-y", "todo add test"], env=dict(env, JEEG_HOME=str(d2)), capture_output=True, text=True, stdin=subprocess.DEVNULL)
    check("existing open folder is tightened", (d2.stat().st_mode & 0o077) == 0)

# ---- archives
w = Path(tempfile.mkdtemp())
evil = w / "evil.zip"
with zipfile.ZipFile(evil, "w") as z:
    z.writestr("../escape.txt", "x")
r = task("unzip file", str(evil))
check("unzip refuses ../ in zip", "unsafe" in r.stdout.lower() and not (w.parent / "escape.txt").exists(), r.stdout)
tev = w / "evil.tar"
with tarfile.open(tev, "w") as t:
    ti = tarfile.TarInfo("link"); ti.type = tarfile.SYMTYPE; ti.linkname = "/etc"; t.addfile(ti)
r = task("unzip file", str(tev))
check("unzip refuses symlinks in tar", "unsafe" in r.stdout.lower(), r.stdout)
tev2 = w / "evil2.tar"
with tarfile.open(tev2, "w") as t:
    ti = tarfile.TarInfo("../../x.txt"); ti.size = 1; t.addfile(ti, io.BytesIO(b"x"))
r = task("unzip file", str(tev2))
check("unzip refuses ../ in tar", "unsafe" in r.stdout.lower(), r.stdout)

# ---- backup import validation
bad = w / "bad.zip"
with zipfile.ZipFile(bad, "w") as z:
    z.writestr("manifest.json", json.dumps({"jeeg": "backup"}))
    z.writestr("routines.json", "{not json")
r = task("import data", str(bad))
check("import refuses invalid JSON", r.returncode != 0 and "not valid JSON" in r.stdout, r.stdout)
check("import wrote nothing", not (jh / "routines.json").exists())
nest = w / "nest.zip"
with zipfile.ZipFile(nest, "w") as z:
    z.writestr("manifest.json", json.dumps({"jeeg": "backup"})); z.writestr("sub/x.json", "{}")
r = task("import data", str(nest))
check("import refuses folders in names", r.returncode != 0 and "Unsafe" in r.stdout, r.stdout)

# ---- crashes become one clear line, never a traceback
for name, arg in (("create_folder", "a" * 3000), ("file_hash", "a" * 3000), ("large_folders", "/etc/passwd"), ("random_number", "0"), ("add_bill", "x 99999999999999999999")):
    r = script(name, arg)
    check(f"{name}: no traceback on hostile input", "Traceback" not in r.stdout + r.stderr, (r.stdout + r.stderr)[-200:])
r = script("large_folders", "/etc/passwd")
check("folder tasks reject a file path clearly", "not a folder" in r.stdout, r.stdout)

# ---- engine input limits
r = task("--dry-run", "open " + "a" * 5000)
check("over-long line refused", r.returncode != 0 and "too long" in r.stdout, r.stdout)
r = task("--dry-run", "open \x1b[31myoutube")
check("control characters stripped", "\x1b" not in r.stdout, repr(r.stdout))

# ---- web requests quote user text
import types
caught = []
fk = types.ModuleType("_net"); fk.get = lambda u, **k: caught.append(u)
sys.modules["_net"] = fk
import runpy
for name, argv in (("crypto_price", ["bit&coin=x#y"]), ("daily_briefing", ["pune?x=1&y=2"])):
    sys.argv = [name + ".py"] + argv
    try: runpy.run_path(str(SCR / (name + ".py")), run_name="__main__")
    except SystemExit: pass
check("crypto request cannot be injected into", caught and "coin=x" not in caught[0] and "#" not in caught[0] and caught[0].count("&") == 2, caught)
check("briefing request quotes text", len(caught) > 1 and "?x=1" not in caught[1], caught)

print(f"security: {total - len(fails)}/{total} passed")
sys.exit(1 if fails else 0)
