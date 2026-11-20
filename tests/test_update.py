"""Self-update from PyPI for an unzipped folder, against a local fake PyPI. Run: python tests/test_update.py"""
import hashlib, http.server, io, json, os, re, shutil, subprocess, sys, tempfile, threading, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
TMP = Path(tempfile.mkdtemp(prefix="jeeg-upd-"))
HOME = TMP / "home"; HOME.mkdir()
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
def make_app(dst):
    dst.mkdir()
    for f in ROOT.glob("jeeg*.py"): shutil.copy(f, dst / f.name)
    shutil.copytree(ROOT / "scripts", dst / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
def make_wheel(version="2.99.0", drop=(), tamper=None, extra=None, few=False):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for f in ROOT.glob("jeeg*.py"):
            t = f.read_text(encoding="utf-8")
            if f.name == "jeeg.py": t = re.sub(r'__version__\s*=\s*"[^"]+"', f'__version__ = "{version}"', t, count=1)
            z.writestr(f.name, t)
        for i, f in enumerate(sorted((ROOT / "scripts").glob("*.py"))):
            if f.name in drop or (few and i > 10): continue
            z.writestr("jeeg_scripts/" + f.name, f.read_text(encoding="utf-8"))
        if tamper: z.writestr("jeeg_scripts/" + tamper, "def broken(:\n")
        for n, t in (extra or {}).items(): z.writestr(n, t)
    return b.getvalue()
STATE = {"wheel": b"", "sha": None, "hits": 0, "version": "2.99.0"}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        STATE["hits"] += 1
        if self.path == "/json":
            sha = STATE["sha"] or hashlib.sha256(STATE["wheel"]).hexdigest()
            body = json.dumps({"info": {"version": STATE["version"]}, "urls": [{"packagetype": "bdist_wheel", "filename": f"jeeg-{STATE['version']}-py3-none-any.whl", "url": f"http://127.0.0.1:{PORT}/w.whl", "digests": {"sha256": sha}, "size": len(STATE["wheel"])}]}).encode()
        else:
            body = STATE["wheel"]
        self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
ENV = {**os.environ, "JEEG_HOME": str(HOME), "HOME": str(TMP), "JEEG_PYPI_API": f"http://127.0.0.1:{PORT}/json"}
def run(app, *a):
    r = subprocess.run([sys.executable, str(app / "jeeg.py")] + list(a), capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL, env=ENV)
    return r.returncode, r.stdout + r.stderr
def snapshot(app): return {str(p.relative_to(app)): p.read_bytes() for p in list(app.glob("jeeg*.py")) + list((app / "scripts").glob("*.py"))}
# ---- check only
app = TMP / "app1"; make_app(app); STATE["wheel"] = make_wheel()
c, o = run(app, "update"); ok(c == 0 and "2.99.0" in o and "update now" in o, "update shows the newer version: " + o)
before = snapshot(app)
c, o = run(app, "update", "now"); ok(c == 3, "update now asks first (rc=%s) %s" % (c, o))
ok(snapshot(app) == before, "nothing changed without a yes")
# ---- real update
c, o = run(app, "--yes", "update now"); ok(c == 0 and "Updated to JeeG 2.99.0" in o, "update applied: " + o)
c, o = run(app, "--version"); ok("2.99.0" in o, "the folder now runs 2.99.0: " + o)
bk = list((HOME / "backups").glob("program-before-*.zip")); ok(bk and "jeeg.py" in zipfile.ZipFile(bk[0]).namelist(), "a copy of the old files was saved")
ok((app / ".jeeg-files.json").is_file(), "manifest written")
c, o = run(app, "update"); ok("up to date" in o, "now up to date: " + o)
# ---- a later release removes a task: the old one is deleted, user data kept
(HOME / "notes.json").write_text('["mine"]')
STATE["version"] = "3.0.0"; STATE["wheel"] = make_wheel("3.0.0", drop=("water_log.py",))
c, o = run(app, "--yes", "update now"); ok(c == 0 and not (app / "scripts" / "water_log.py").exists(), "a removed task is deleted: " + o)
ok((HOME / "notes.json").read_text() == '["mine"]', "your data is never touched")
# ---- bad downloads are refused and change nothing
def refused(label, version, **kw):
    a = TMP / ("app-" + label); make_app(a); snap = snapshot(a)
    STATE["version"] = version; STATE["wheel"] = make_wheel(version, **kw); STATE["sha"] = kw.pop("sha", None)
    c, o = run(a, "--yes", "update", "now"); ok(c == 1 and snapshot(a) == snap, f"{label} refused, files unchanged: rc={c} {o[-120:]}")
    return a
STATE["sha"] = "0" * 64; STATE["version"] = "4.0.0"; STATE["wheel"] = make_wheel("4.0.0")
a = TMP / "app-sha"; make_app(a); snap = snapshot(a); c, o = run(a, "--yes", "update", "now")
ok(c == 1 and "checksum" in o and snapshot(a) == snap, "wrong checksum refused: " + o); STATE["sha"] = None
refused("syntax", "4.0.0", tamper="evil_task.py")
refused("fewfiles", "4.0.0", few=True)
a = TMP / "app-ver"; make_app(a); snap = snapshot(a); STATE["version"] = "4.1.0"; STATE["wheel"] = make_wheel("4.0.0")
c, o = run(a, "--yes", "update", "now"); ok(c == 1 and snapshot(a) == snap, "wheel whose version differs from PyPI's claim refused: " + o)
a = TMP / "app-trav"; make_app(a); STATE["version"] = "4.2.0"; STATE["wheel"] = make_wheel("4.2.0", extra={"jeeg_scripts/../../evil.py": "x = 1\n", "../evil2.py": "x = 1\n", "jeeg_scripts/sub/x.py": "x = 1\n"})
c, o = run(a, "--yes", "update", "now"); ok(c == 0 and not (TMP / "evil.py").exists() and not (TMP.parent / "evil2.py").exists() and not (a / "scripts" / "sub").exists() and not (a.parent / "evil.py").exists(), "path tricks inside the wheel are ignored: " + o)
# ---- the optional daily notice
import jeeg_cmds
STATE["version"] = "9.9.9"; STATE["wheel"] = make_wheel("9.9.9"); os.environ["JEEG_PYPI_API"] = ENV["JEEG_PYPI_API"]
st = TMP / "st"; st.mkdir(); STATE["hits"] = 0
jeeg_cmds.update_notice(st, TMP / "app1", "2.20.0"); ok(STATE["hits"] == 0, "off by default: no request is made")
c, o = run(app, "update", "auto", "on"); ok("never installs by itself" in o, "auto on")
(st / "update_check.json").write_text('{"on": true}')
import contextlib
buf = io.StringIO()
with contextlib.redirect_stderr(buf): jeeg_cmds.update_notice(st, TMP / "app1", "2.20.0")
ok("9.9.9" in buf.getvalue() and STATE["hits"] == 1, "one line, one request: %r hits=%s" % (buf.getvalue(), STATE["hits"]))
buf = io.StringIO()
with contextlib.redirect_stderr(buf): jeeg_cmds.update_notice(st, TMP / "app1", "2.20.0")
ok(buf.getvalue() == "" and STATE["hits"] == 1, "only once a day")
c, o = run(app, "update", "auto", "off"); ok("off" in o.lower(), "auto off")
sys.path.insert(0, str(ROOT)); import jeeg_api, jeeg_remote
ok("update" in jeeg_api.TERMINAL_ONLY and "update" in jeeg_remote.TERMINAL_ONLY, "an AI can never update JeeG")
srv.shutdown(); shutil.rmtree(TMP, ignore_errors=True)
print(f"{P} passed, {F} failed"); sys.exit(1 if F else 0)
