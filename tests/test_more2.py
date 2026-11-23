"""timer source, link who / broadcast, iot status, channel export / search. Run: python tests/test_more2.py"""
import http.server, json, os, signal, subprocess, sys, tempfile, threading, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
TMP = Path(tempfile.mkdtemp(prefix="jeeg-m2-")); (TMP / "home").mkdir()
os.environ["HOME"] = os.environ["USERPROFILE"] = str(TMP / "home")
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
env = dict(os.environ, JEEG_HOME=str(TMP / "h"))
def jeeg(*a, e=None, cwd=None):
    p = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=e or env, timeout=90, stdin=subprocess.DEVNULL, cwd=cwd or TMP)
    return p.returncode, p.stdout + p.stderr

# ---- timer source
for bad in ("every 5 seconds", "every 0 minutes", "every 9 days", "every x minutes", "every minute"):
    rc, o = jeeg("bridge", "add", "t", "when", *bad.split(), "then", "notify x"); ok(rc != 0, "timer refused: " + bad)
rc, o = jeeg("bridge", "add", "tick", "when", "every", "10", "seconds", "then", "channel post lab tick-{msg}"); ok(rc == 0 and "every 10 seconds" in o, "timer rule: " + o)
rc, o = jeeg("bridge", "list"); ok("every 10 seconds" in o, "listed")
proc = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "bridge", "run"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, stdin=subprocess.DEVNULL, start_new_session=True)
time.sleep(24)
os.killpg(proc.pid, signal.SIGINT)
try: out = proc.communicate(timeout=20)[0]
except subprocess.TimeoutExpired: os.killpg(proc.pid, signal.SIGKILL); out = proc.communicate()[0]; ok(False, "bridge did not stop")
lines = (TMP / "h" / "channels" / "lab.jsonl").read_text().splitlines() if (TMP / "h" / "channels" / "lab.jsonl").exists() else []
ok(len(lines) == 2 and "tick-tick" in lines[0], "timer fired twice in 24 s: %d %s" % (len(lines), out[-300:]))

# ---- channel export / search
rc, o = jeeg("channel", "post", "lab", "as", "claude:", "the deploy finished")
rc, o = jeeg("channel", "search", "deploy"); ok("[lab]" in o and "claude@" in o and "1 match" in o, "search: " + o)
rc, o = jeeg("channel", "search", "zzz"); ok("0 match" in o, "search none")
rc, o = jeeg("channel", "export", "lab"); ok(rc == 0 and (TMP / "channel_lab.txt").exists() and "the deploy finished" in (TMP / "channel_lab.txt").read_text(), "export: " + o)
rc, o = jeeg("channel", "export", "lab"); ok(rc != 0 and "already exists" in o, "export never overwrites")
rc, o = jeeg("channel", "export", "nothing"); ok(rc != 0, "export of nothing")

# ---- iot status (fake Shelly)
STATE = {"on": True}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if "Switch.Set" in self.path: STATE["on"] = "on=true" in self.path
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(json.dumps({"output": STATE["on"]}).encode())
srv = http.server.HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
rc, o = jeeg("iot", "status"); ok("No smart devices" in o, "no devices")
jeeg("device", "add", "lamp", "shelly", f"127.0.0.1:{srv.server_port}"); jeeg("device", "add", "ghost", "tasmota", "127.0.0.1:11")
rc, o = jeeg("iot", "status"); ok("lamp" in o and "ON" in o and "ghost" in o and "not reachable" in o and "1 on, 0 off, 1 not reachable" in o, "iot status: " + o)
STATE["on"] = False
rc, o = jeeg("iot", "status"); ok("1 on" not in o and "1 off" in o, "iot status sees off: " + o)

# ---- link who / broadcast
import jeeg_link as L
A, B, C = TMP / "A", TMP / "B", TMP / "C"
for d in (A, B, C): d.mkdir()
for d, n in ((A, "alpha"), (B, "beta"), (C, "gamma")): L.Store(d).set_name(n)
def listener(d):
    l = L.Listener(d, port=0, out=lambda s: None, interactive=True); a = iter(["y", "chat", "y", "chat"]); l.prompt = lambda t, default="": next(a, default)
    threading.Thread(target=l.serve, daemon=True).start(); l.ready.wait(5); return l
la, lb = listener(A), listener(B)
for target, tl in ((B, la), (C, la)):
    try: L._cmd_pair(L.Store(target), [f"127.0.0.1:{tl.port}"], True, lambda s: None, lambda p: "y" if "number" in p else "chat")
    except Exception as ex: print("pair error", ex)
    time.sleep(0.3)
# from alpha's side: A paired as responder twice; give each peer an address (beta listens, gamma does not)
d = L.Store(A).peers()
for pid, r in d.items():
    r["addr"] = f"127.0.0.1:{lb.port}" if r["name"] == "beta" else "127.0.0.1:11"
L.Store(A).save_peers(d)
ea = dict(env, JEEG_HOME=str(A))
rc, o = jeeg("link", "who", e=ea); ok("beta" in o and "online" in o and "gamma" in o and "not reachable" in o, "who: " + o)
rc, o = jeeg("link", "broadcast", "hello everyone", e=ea); ok(rc == 0 and "beta" in o and "delivered" in o and "not delivered" in o, "broadcast: " + o)
ok(any(m["text"] == "hello everyone" for m in L.Store(B).inbox(5)), "beta received the broadcast")
rc, o = jeeg("link", "broadcast", e=ea); ok(rc != 0, "needs text")
eb = dict(env, JEEG_HOME=str(TMP / "empty"))
rc, o = jeeg("link", "who", e=eb); ok("No paired" in o, "who with nobody")
print(f"more2: {P} passed, {F} failed"); sys.exit(1 if F else 0)
