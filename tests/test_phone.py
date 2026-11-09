"""Phone page: safe mode (default) and god mode (every task, PIN, time limit, confirmation button)."""
import json, os, re, socket, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
HOME = tempfile.mkdtemp(prefix="jeeg-ph-"); os.environ["JEEG_HOME"] = HOME
WORK = Path(tempfile.mkdtemp(prefix="jeeg-ph-w-"))
P = F = 0
def ok(c, label):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", label)
def freeport():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def start(*words):
    port = freeport()
    proc = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "web", *words, str(port)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK)
    lines = []
    for _ in range(20):
        ln = proc.stdout.readline(); lines.append(ln)
        if "Ctrl+C stops it" in ln or "Press Ctrl+C to stop" in ln: break
    text = "".join(lines)
    m = re.search(r"http://([\d.]+):(\d+)/\?k=(\S+)", text)
    return proc, port, text, m

class Client:
    def __init__(self, ip, port, key): self.base, self.key, self.tok = f"http://{ip}:{port}", key, None
    def get(self, path, headers=None):
        try:
            with urllib.request.urlopen(urllib.request.Request(self.base + path, headers=headers or {}), timeout=10) as r: return r.status, r.read().decode()
        except urllib.error.HTTPError as e: return e.code, e.read().decode()
    def open(self):
        st, page = self.get(f"/?k={self.key}")
        m = re.search(r'const T="([^"]+)",MODE="([^"]+)"', page)
        self.tok, self.mode = (m.group(1), m.group(2)) if m else (None, None)
        return st, page
    def run(self, q, pin=None, yes=False, host=None, origin=None):
        h = {"Content-Type": "application/json", "X-JeeG-Token": self.tok}
        if pin is not None: h["X-JeeG-Pin"] = pin
        if host: h["Host"] = host
        if origin: h["Origin"] = origin
        try:
            with urllib.request.urlopen(urllib.request.Request(self.base + "/run", json.dumps({"q": q, "yes": yes}).encode(), h), timeout=60) as r: return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            try: return e.code, json.loads(e.read())
            except ValueError: return e.code, {}

# ---------------------------------------------------------------- safe mode still safe, and says so
proc, port, text, m = start("lan")
try:
    ok(m is not None and "Safe mode" in text and "GOD" not in text, "safe mode banner " + text[:80])
    c = Client(m.group(1), port, m.group(3)); st, page = c.open()
    ok(st == 200 and c.mode == "safe", "safe page mode")
    ok("GOD MODE" in page and 'id="gb" hidden' in page, "god banner exists but is hidden in safe mode")
    st, j = c.run("open youtube"); ok("not allowed" in j.get("out", ""), "safe: open youtube refused")
    st, j = c.run("gst 100 18", pin="123456"); ok("18.00" in j.get("out", ""), "safe: a pin header is ignored")
finally:
    proc.terminate(); proc.wait(timeout=10)

# ---------------------------------------------------------------- god mode
proc, port, text, m = start("lan", "god")
try:
    ok(m is not None and "GOD MODE" in text, "god banner printed")
    pm = re.search(r"PIN : (\d{6})", text); pin = pm.group(1) if pm else ""
    ok(len(pin) == 6, "six digit pin printed")
    ok("closes by itself in 30 minutes" in text and "plain http" in text and "5 wrong PINs" in text, "warnings printed")
    c = Client(m.group(1), port, m.group(3))
    ok(c.get("/")[0] == 403, "god page needs the link key")
    st, page = c.open(); ok(st == 200 and c.mode == "god", "god page opens")
    m2 = re.search(r"END=Date.now\(\)\+(\d+)\*1000", page); ok(m2 and 1700 <= int(m2.group(1)) <= 1800, "page knows the time left")
    ok(c.get(f"/?k={c.key}", {"Host": "evil.example"})[0] == 403, "god: host check")
    ok(c.run("gst 100 18", pin=pin, host="evil.example")[0] == 403, "god: POST host check")
    ok(c.run("gst 100 18", pin=pin, origin="http://evil.example")[0] == 403, "god: origin check")
    st, j = c.run("gst 100 18", pin=None); ok(st == 403 and "Wrong PIN" in j.get("out", ""), "god: no PIN refused")
    st, j = c.run("gst 100 18", pin="000000" if pin != "000000" else "111111"); ok(st == 403 and "tries left" in j.get("out", ""), "god: wrong PIN refused")
    # every task, no restriction
    (WORK / "d.json").write_text('{"secret_value": 42}')
    st, j = c.run("gst 100 18", pin=pin); ok(st == 200 and "18.00" in j["out"], "god runs a normal task")
    st, j = c.run("json format " + str(WORK / "d.json"), pin=pin); ok("secret_value" in j.get("out", ""), "god can read a file: " + str(j)[:80])
    st, j = c.run("open youtube", pin=pin); ok("not allowed" not in j.get("out", "") and st == 200, "god: open youtube is allowed: " + str(j)[:80])
    st, j = c.run("hash text hello", pin=pin); ok("2cf24dba" in j.get("out", ""), "god: hash text")
    st, j = c.run("calculate 2+2 then save it to a note", pin=pin); ok(st == 200 and "only available in the terminal" not in j.get("out", ""), "god: chaining allowed")
    for q in ("update", "plugin install x", "setup", "web", "autorun add x", "report", "share plugin x"):
        st, j = c.run(q, pin=pin); ok("only available in the terminal" in j.get("out", ""), f"god: terminal-only {q!r}")
    # confirmation button flow
    c.run("shopping add milk", pin=pin); c.run("shopping add eggs", pin=pin)
    st, j = c.run("shopping clear", pin=pin)
    ok(j.get("confirm") is True and "confirmation" in j["out"], "god: confirm task asks first: " + str(j)[:100])
    st, j = c.run("shopping list", pin=pin); ok("milk" in j["out"], "nothing was cleared before confirming")
    st, j = c.run("shopping clear", pin=pin, yes=True); ok(j.get("confirm") is not True and st == 200, "god: confirmed task runs: " + str(j)[:100])
    st, j = c.run("shopping list", pin=pin); ok("milk" not in j["out"], "confirmed clear happened")
    ok(c.run("shopping clear", pin=pin, yes="true")[1].get("confirm") is True, "yes must be the JSON value true, not a string")
    # lockout after 5 wrong PINs (the good PIN is then refused too)
    for i in range(5): c.run("gst 1 1", pin="999999" if pin != "999999" else "888888")
    st, j = c.run("gst 100 18", pin=pin); ok(st == 429 and "Locked" in j.get("out", ""), "god: locked after wrong PINs: " + str(st) + str(j)[:60])
finally:
    proc.terminate()
    try: out = proc.communicate(timeout=10)[0]
    except Exception: out = ""
ok("WRONG PIN" in out and "json format" in out and "[confirmed]" in out, "every command and wrong PIN is printed in the terminal")
ok(pin not in (out.split("Ctrl+C stops it")[-1] if "Ctrl+C stops it" in out else ""), "the PIN is not repeated in the log")

# ---------------------------------------------------------------- the time limit really ends it
import jeeg_cmds
port = freeport(); out = []
t = threading.Thread(target=jeeg_cmds.serve, args=(ROOT, Path(HOME), port), kwargs=dict(open_browser=False, lan=True, god=True, minutes=0.04), daemon=True)
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    t.start(); time.sleep(1.0)
text = buf.getvalue(); m = re.search(r"http://([\d.]+):(\d+)/\?k=(\S+)", text); pin = re.search(r"PIN : (\d{6})", text).group(1)
c = Client(m.group(1), port, m.group(3)); c.open()
st, j = c.run("gst 100 18", pin=pin); ok(st == 200 and "18.00" in j["out"], "works before the limit")
time.sleep(2.6)
st, j = c.run("gst 100 18", pin=pin); ok(st == 403 and "ended" in j.get("out", ""), "refused after the time limit: " + str(st) + str(j)[:60])
t.join(timeout=5); ok(not t.is_alive(), "the server stops itself after the time limit")

# ---------------------------------------------------------------- command line
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "web god"], capture_output=True, text=True, env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, timeout=30)
ok(r.returncode == 1 and "web lan god" in r.stdout, "web god alone explains itself: " + r.stdout[:80])
sys.path.insert(0, str(ROOT))
import jeeg
src = (ROOT / "jeeg.py").read_text()
ok('(?:\\s+(god|full|everything))?' in src, "god option is parsed")

print(f"phone page tests: {P} passed, {F} failed")
sys.exit(1 if F else 0)
