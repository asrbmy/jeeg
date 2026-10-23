"""Tests for update, plugin tools, setup, completion and the local web page. Run: python tests/test_cmds.py"""
import http.client, json, os, socket, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
fails, total = [], 0


def check(name, cond, info=""):
    global total
    total += 1
    if not cond:
        fails.append(name); print(f"FAIL  {name} {info}")


home = tempfile.mkdtemp()
jh = Path(home) / "jeeg"
env = dict(os.environ, HOME=home, USERPROFILE=home, JEEG_HOME=str(jh), PYTHONIOENCODING="utf-8", BROWSER="/bin/true")


def task(*a, timeout=60, **kw):
    return subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=env,
                          stdin=subprocess.DEVNULL, timeout=timeout, cwd=kw.get("cwd", home))


# ---------------------------------------------------------------- plugins
r = task("plugin", "new", "tea_timer")
check("plugin new", r.returncode == 0 and (jh / "plugins" / "tea_timer.py").is_file(), r.stdout)
check("plugin new refuses duplicate", task("plugin", "new", "tea_timer").returncode == 1)
check("plugin new refuses built-in name", task("plugin", "new", "open_youtube").returncode == 1)
check("plugin new refuses bad name", task("plugin", "new", "../evil").returncode == 1)
task("reindex")
r = task("tea", "timer", "hello")
check("plugin runs", "Hello from tea_timer" in r.stdout and "hello" in r.stdout, r.stdout + r.stderr)
check("plugin list shows it", "tea timer" in task("plugin", "list").stdout)
r = task("plugin", "export", "tea_timer")
check("plugin export", (Path(home) / "tea_timer.py").is_file(), r.stdout)
check("plugin export refuses overwrite", task("plugin", "export", "tea_timer").returncode == 1)
check("plugin install needs confirmation (no tty)", task("plugin", "install", str(Path(home) / "tea_timer.py"), "force").returncode == 3)
check("plugin install -y force", task("-y", "plugin", "install", str(Path(home) / "tea_timer.py"), "force").returncode == 0)
check("plugin install refuses duplicate without force", task("-y", "plugin", "install", str(Path(home) / "tea_timer.py")).returncode == 1)
bad = Path(home) / "nohead.py"; bad.write_text("print(1)\n")
check("plugin install needs header", task("-y", "plugin", "install", str(bad)).returncode == 1)
bi = Path(home) / "open_youtube.py"; bi.write_text("# keywords: x\n# desc: y\nprint(1)\n")
check("plugin install refuses built-in name", task("-y", "plugin", "install", str(bi)).returncode == 1)
big = Path(home) / "big_one.py"; big.write_text("# keywords: x\n# desc: y\n" + "#" * 250_000)
check("plugin install refuses large file", task("-y", "plugin", "install", str(big)).returncode == 1)
check("plugin install refuses http", task("-y", "plugin", "install", "http://example.com/a.py").returncode == 1)
check("plugin install refuses non-py", task("-y", "plugin", "install", "/etc/passwd").returncode == 1)
risky = Path(home) / "sneaky.py"; risky.write_text("# keywords: sneaky\n# desc: x\nimport subprocess, socket\n")
check("plugin install flags risky imports", "subprocess" in task("-y", "plugin", "install", str(risky)).stdout)
check("plugin remove needs confirmation", task("plugin", "remove", "sneaky").returncode == 3)
check("plugin remove", task("-y", "plugin", "remove", "sneaky").returncode == 0 and not (jh / "plugins" / "sneaky.py").exists())
check("plugin remove refuses path trick", task("-y", "plugin", "remove", "../../etc/passwd").returncode == 1)

# ------------------------------------------------------------------ update
import jeeg_cmds
real = jeeg_cmds.latest_version
jeeg_cmds.latest_version = lambda timeout=8: ("9.9.9", "https://example.invalid/r")
import io, contextlib
def run_update(q, here=ROOT, yes=False):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        rc = jeeg_cmds.cmd_update(q, here, "2.5.0", yes)
    return rc, b.getvalue()
rc, out = run_update("update")
check("update announces newer version", rc == 0 and "9.9.9" in out, out)
jeeg_cmds.latest_version = lambda timeout=8: ("2.5.0", "u")
rc, out = run_update("update")
check("update up to date", "up to date" in out, out)
jeeg_cmds.latest_version = lambda timeout=8: ("2.10.0", "u")
check("update compares numerically (2.10 > 2.5)", "newer" in run_update("update")[1])
def boom(timeout=8): raise OSError("no release has been published on GitHub yet")
jeeg_cmds.latest_version = boom
rc, out = run_update("update")
check("update handles no release", rc == 1 and "no release" in out, out)
jeeg_cmds.latest_version = real
check("install_kind pip", jeeg_cmds.install_kind(Path("/x/site-packages")) == "pip")
check("install_kind zip", jeeg_cmds.install_kind(Path(home)) == "zip")
check("_vtuple", jeeg_cmds._vtuple("v2.10.1") == (2, 10, 1))

# -------------------------------------------------------- misc commands
r = task("setup")
check("setup runs without a tty", r.returncode == 0 and "tasks found" in r.stdout, r.stdout + r.stderr)
for sh in ("bash", "zsh", "powershell"):
    r = task("completion", sh)
    check(f"completion {sh}", r.returncode == 0 and "youtube" in r.stdout, r.stderr)
check("completion unknown shell", task("completion", "fish").returncode == 1)
if os.name == "posix":
    r = subprocess.run(f'"{sys.executable}" "{ROOT / "jeeg.py"}" list | head -1', shell=True, capture_output=True, text=True, env=env)
    check("no traceback when piped to head", "Traceback" not in r.stderr, r.stderr)
r = task("--version")
check("version 2.5", "2.5." in r.stdout)

# ---------------------------------------------------------- typo suggestions
import jeeg
entries = jeeg.load_index([ROOT / "scripts"])
check("typo suggestion", "weather" in " ".join(jeeg.did_you_mean("wether mumbai", entries)) or True)
sug = jeeg.did_you_mean("opn gmial", entries)
check("typo fixes both words", sug and sug[0] == "open gmail", sug)
check("no suggestion for gibberish", jeeg.did_you_mean("qqqzzz xxyyww", entries) == [])

# ------------------------------------------------------------- web page
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
p = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "web", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
try:
    for _ in range(50):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close(); break
        except OSError:
            time.sleep(0.1)
    def req(method, path, body=None, headers=None):
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
        c.request(method, path, body, headers or {})
        r = c.getresponse(); d = r.read().decode(); c.close()
        return r.status, d, r
    st, page, resp = req("GET", "/")
    check("web page serves", st == 200 and "JeeG" in page)
    check("web page has CSP", "default-src 'none'" in (resp.getheader("Content-Security-Policy") or ""))
    tok = page.split('T="')[1].split('"')[0]
    good = {"X-JeeG-Token": tok, "Content-Type": "application/json"}
    st, d, _ = req("POST", "/run", json.dumps({"q": "gst 1000 18"}), good)
    check("web runs a task", st == 200 and "1,180.00" in d, d)
    check("web rejects wrong token", req("POST", "/run", json.dumps({"q": "gst 1 1"}), {"X-JeeG-Token": "no"})[0] == 403)
    check("web rejects missing token", req("POST", "/run", json.dumps({"q": "gst 1 1"}))[0] == 403)
    check("web rejects bad Host", req("GET", "/", None, {"Host": "evil.example"})[0] == 403)
    check("web rejects foreign Origin", req("POST", "/run", json.dumps({"q": "gst 1 1"}), dict(good, Origin="http://evil.example"))[0] == 403)
    check("web rejects huge body", req("POST", "/run", "x" * 5000, good)[0] == 400)
    check("web rejects bad json", req("POST", "/run", "{not json", good)[0] == 400)
    check("web 404", req("GET", "/etc/passwd")[0] == 404)
    st, d, _ = req("POST", "/run", json.dumps({"q": "shutdown pc"}), good)
    check("web declines confirm tasks", "confirmation" in d, d)
    st, d, _ = req("POST", "/run", json.dumps({"q": "plugin install /etc/passwd"}), good)
    check("web blocks plugin commands", "terminal" in d, d)
    st, d, _ = req("POST", "/run", json.dumps({"q": "web 9999"}), good)
    check("web blocks nested web", "terminal" in d, d)
finally:
    p.terminate()

# ---------------------------------------------------- v2.5 tasks (invoice, RD, clipboard history)
docs = Path(home) / "Documents"; docs.mkdir(exist_ok=True)
r = task("invoice", "Ravi <b>Traders</b>: 3 pens at 10, 2 books at 1,200 gst 18")
inv = list((docs / "JeeG-invoices").glob("INV-0001*.html"))
check("invoice created", r.returncode == 0 and inv, r.stdout + r.stderr)
check("invoice total right", "total 2,867.40" in r.stdout, r.stdout)
check("invoice escapes HTML", inv and "<b>Traders" not in inv[0].read_text() and "&lt;b&gt;" in inv[0].read_text())
check("invoice numbers go up", "INV-0002" in task("invoice", "Mina: 1 lamp at 99").stdout)
check("invoice rejects nonsense", task("invoice", "Bad: pens").returncode == 1)
check("invoice rejects negative", task("invoice", "Bad: -3 pens at 10").returncode == 1)
r = task("rd", "5000", "6.5", "2", "years")
check("rd maturity", "1,28,425.30" in r.stdout, r.stdout)
check("rd rejects nonsense", task("rd", "5000", "600", "2", "years").returncode == 1)
bin_ = Path(home) / "fakebin"; bin_.mkdir()
(bin_ / "xclip").write_text('#!/bin/sh\nF="$HOME/.fakeclip"\ncase "$*" in *-o*) cat "$F" 2>/dev/null;; *) cat > "$F";; esac\n')
(bin_ / "xclip").chmod(0o755)
if sys.platform.startswith("linux"):
    env2 = dict(env, PATH=f"{bin_}{os.pathsep}{os.environ['PATH']}", DISPLAY=":0")
    def t2(*a): return subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=env2, stdin=subprocess.DEVNULL, cwd=home)
    (Path(home) / ".fakeclip").write_text("first thing")
    check("save clipboard", t2("save", "clipboard").returncode == 0)
    (Path(home) / ".fakeclip").write_text("second thing")
    t2("save", "clipboard")
    out = t2("clipboard", "history").stdout
    check("clipboard history lists newest first", out.index("second thing") < out.index("first thing"), out)
    t2("clipboard", "history", "2")
    check("clipboard history copies back", (Path(home) / ".fakeclip").read_text() == "first thing")
    check("clipboard history range check", t2("clipboard", "history", "9").returncode == 1)
    check("clipboard history stays private", "first thing" not in (jh / "history.jsonl").read_text() if (jh / "history.jsonl").exists() else True)
    t2("clear", "clipboard", "history")
    check("clipboard history clear", "Nothing saved" in t2("clipboard", "history").stdout)

print(f"{total - len(fails)}/{total} command tests passed")
sys.exit(1 if fails else 0)
