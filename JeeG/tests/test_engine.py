"""Tests for aliases, explain, did-you-mean, logs and the installer.
Run:  python tests/test_engine.py   (uses a temporary data folder; touches nothing of yours)"""
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMP = tempfile.mkdtemp()
os.environ["JEEG_HOME"] = TMP
spec = importlib.util.spec_from_file_location("jeeg", ROOT / "jeeg.py")
tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)
entries = tr.load_index(tr.script_dirs([]), rebuild=True)
fails = []
total = 0


def check(name, cond, info=""):
    global total
    total += 1
    if not cond:
        fails.append(name)
        print(f"FAIL  {name} {info}")


def run(line):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = tr.handle(line, tr.script_dirs([]), {"yes": True, "dry": True, "timeout": None})
    return rc, buf.getvalue()


# ---- aliases
rc, out = run("alias add zqx = open youtube")
check("alias saved", rc == 0 and "Saved" in out)
rc, out = run("zqx")
check("alias runs", "open_youtube.py" in out, out)
rc, out = run("alias add wa = send whatsapp to")
rc, out = run("wa mom hello")
check("alias keeps extra words", "send_whatsapp.py to mom hello" in out, out)
rc, out = run("alias add list = open youtube")
check("reserved word refused", rc == 1 and "built-in" in out)
rc, out = run("alias add bad = flibbertigibbet nonsense")
check("alias to nothing refused", rc == 1)
rc, out = run("alias list")
check("alias list", "zqx" in out and "wa" in out)
rc, out = run("alias remove zqx")
check("alias removed", rc == 0)
rc, out = run("zqx")
check("removed alias no longer expands", "open_youtube.py" not in out or "No matching" in out, out)

# ---- explain, misses, did-you-mean
rc, out = run("explain open youtube")
check("explain shows winner", "open youtube" in out and "would run" in out, out)
rc, out = run("explain flibbertigibbet")
check("explain none", rc == 1 and "No task matches" in out)
check("did you mean", "open youtube" in tr.did_you_mean("open youtub", entries))
rc, out = run("flibbertigibbet zzz")
check("miss reported", rc == 1 and "No matching task" in out)
rc, out = run("misses")
check("miss logged", "flibbertigibbet zzz" in out, out)

# ---- run log and stats
e = next(x for x in entries if x["name"] == "show_path")
tr.log_run(e, 0, 0.1)
rc, out = run("stats")
check("stats", "show path" in out, out)

# ---- doctor
rc, out = run("doctor")
check("doctor runs", "Python" in out and "tasks from" in out, out)

# ---- installer
home = tempfile.mkdtemp()
env = dict(os.environ, HOME=home, USERPROFILE=home, LOCALAPPDATA=home)
r = subprocess.run([sys.executable, str(ROOT / "install.py"), "--name", "jeegtest"], capture_output=True, text=True, env=env)
check("installer ran", r.returncode == 0, r.stdout + r.stderr)
made = list(Path(home).rglob("jeegtest*"))
check("launcher written", len(made) == 1 and "jeeg.py" in made[0].read_text(), str(made))
if made and os.name != "nt":
    out = subprocess.run([str(made[0]), "--version"], capture_output=True, text=True, env=env)
    check("launcher works", "JeeG" in out.stdout, out.stdout + out.stderr)
r = subprocess.run([sys.executable, str(ROOT / "install.py"), "--name", "tr"], capture_output=True, text=True, env=env)
check("installer accepts valid short name", r.returncode == 0)
r = subprocess.run([sys.executable, str(ROOT / "install.py"), "--uninstall", "--name", "tr"], capture_output=True, text=True, env=env)
r = subprocess.run([sys.executable, str(ROOT / "install.py"), "--uninstall", "--name", "jeegtest"], capture_output=True, text=True, env=env)
check("uninstall", not list(Path(home).rglob("jeegtest*")))

# ---- v2.3 features: packs, tips, routines with args, export/import
rc, out = run("pack off backup")
check("pack off", rc == 0 and "backup" in out.lower())
rc, out = run("export data")
check("disabled pack hides its tasks", "export_data.py" not in out, out[:120])
rc, out = run("pack on backup")
check("pack on", rc == 0)
rc, out = run("pack list")
check("pack list shows categories", "developer" in out and "tasks" in out)
rc, out = run("tips")
check("tips prints a task", rc == 0 and "Try:" in out)

env2 = dict(os.environ, JEEG_HOME=tempfile.mkdtemp(), PYTHONIOENCODING="utf-8")
def cli(*a, inp=""):
    return subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "-y", *a], capture_output=True, text=True, env=env2, input=inp, timeout=60)
Path(env2["JEEG_HOME"]).mkdir(exist_ok=True)
(Path(env2["JEEG_HOME"]) / "routines.json").write_text('{"morning": ["echo hello {1}"]}')
r = cli("run routine morning")
check("routine missing arg fails", r.returncode != 0 and "extra word" in (r.stdout + r.stderr), r.stdout + r.stderr)

# export/import roundtrip
(Path(env2["JEEG_HOME"]) / "notes.txt").write_text("remember milk\n")
zdir = tempfile.mkdtemp()
r = cli("export data", zdir)
zips = list(Path(zdir).glob("*.zip"))
check("export creates zip", r.returncode == 0 and len(zips) == 1, r.stdout + r.stderr)
if zips:
    (Path(env2["JEEG_HOME"]) / "notes.txt").write_text("changed\n")
    r = cli("import data", str(zips[0]))
    check("import restores", (Path(env2["JEEG_HOME"]) / "notes.txt").read_text() == "remember milk\n", r.stdout + r.stderr)
    import zipfile
    evil = Path(zdir) / "evil.zip"
    with zipfile.ZipFile(evil, "w") as z:
        z.writestr("../escape.txt", "x")
    r = cli("import data", str(evil))
    check("evil zip rejected", not (Path(zdir).parent / "escape.txt").exists())

print(f"engine: {total - len(fails)}/{total} passed")
sys.exit(1 if fails else 0)
