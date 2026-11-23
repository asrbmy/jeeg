"""playbook, notify, setup check, setup home, receipts, family board, backup share. Run: python tests/test_extras.py"""
import json, os, socket, subprocess, sys, tempfile, threading, time, zipfile, http.server
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
TMP = Path(tempfile.mkdtemp(prefix="jeeg-extras-"))
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
env = dict(os.environ, JEEG_HOME=str(TMP / "h"), HOME=str(TMP / "home")); (TMP / "home").mkdir()
def jeeg(*a, e=None, cwd=None):
    p = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=e or env, timeout=90, stdin=subprocess.DEVNULL, cwd=cwd or TMP)
    return p.returncode, p.stdout + p.stderr

# ---- playbook
rc, o = jeeg("playbook", "list"); ok("No playbooks" in o, "empty")
rc, o = jeeg("playbook", "add", "calc", "=", "gst 100 18 ; 25 * 4"); ok(rc == 0 and "2 steps" in o, "add: " + o)
rc, o = jeeg("playbook", "show", "calc"); ok("gst 100 18" in o, "show")
rc, o = jeeg("playbook", "run", "calc"); ok(rc == 0 and "118.00" in o and "= 100" in o and "done" in o, "run: " + o)
for bad in ("update now", "link send x hi", "bridge run", "playbook add x = gst 1 1", "shutdown pc", "delete file x", "audit clear", "browser go x"):
    rc, o = jeeg("playbook", "add", "bad", "=", bad); ok(rc != 0, "refused step: " + bad)
rc, o = jeeg("playbook", "add", "stop", "=", "gst 100 18 ; zzzz qqqq ; 2 + 2"); ok(rc == 0, "add with a bad middle step")
rc, o = jeeg("playbook", "run", "stop"); ok(rc != 0 and "Stopped at step 2" in o and "= 4" not in o, "a failing step stops the rest: " + o)
for who in ("JEEG_VIA_AI", "JEEG_VIA_PEER", "JEEG_VIA_BRIDGE"):
    rc, o = jeeg("playbook", "add", "x", "=", "gst 1 1", e=dict(env, **{who: "1"})); ok(rc != 0 and "only be added" in o, f"{who} cannot add")
    rc, o = jeeg("playbook", "remove", "calc", e=dict(env, **{who: "1"})); ok(rc != 0, f"{who} cannot remove")
rc, o = jeeg("playbook", "run", "calc", e=dict(env, JEEG_VIA_AI="1")); ok(rc == 0 and "118.00" in o, "an AI may run a saved playbook")
f = TMP / "h" / "conn_playbooks.json"; d = json.loads(f.read_text()); d["evil"] = ["update apps"]; f.write_text(json.dumps(d))
rc, o = jeeg("playbook", "run", "evil"); ok(rc != 0 and "cannot start with" in o, "hand-edited playbook checked when run")
rc, o = jeeg("playbook", "remove", "calc"); ok(rc == 0, "remove")

# ---- notify
rc, o = jeeg("notify", "me", "dinner", "is", "ready"); ok(rc == 0 and "dinner is ready" in o, "notify: " + o)
rc, o = jeeg("notify", "due"); ok("notify" not in o.lower() or "dinner" not in o, "notify due still goes to the old task")

# ---- receipts
rc, o = jeeg("receipt", "add", "450", "groceries", "Big", "Bazaar", "2026-11-05"); ok(rc == 0 and "Receipt 1" in o, "add: " + o)
rc, o = jeeg("receipt", "add", "1,200.50", "fuel", "Shell", "2026-11-09"); ok(rc == 0, "add 2")
rc, o = jeeg("receipt", "add", "300", "groceries", "Market", "2026-12-01"); ok(rc == 0, "add 3")
rc, o = jeeg("receipt", "add", "-5", "x", "y"); ok(rc != 0, "negative refused")
rc, o = jeeg("receipt", "add", "5", "x", "y", "2026-13-45"); ok(rc != 0, "bad date refused")
rc, o = jeeg("receipt", "total", "2026-11"); ok("1,650.50" in o and "groceries" in o and "2 receipt" in o, "month total: " + o)
rc, o = jeeg("receipt", "total", "2026"); ok("1,950.50" in o, "year total")
rc, o = jeeg("receipt", "total", "nov"); ok(rc != 0, "bad period")
pic = TMP / "bill.png"; pic.write_bytes(b"\x89PNG fake")
rc, o = jeeg("receipt", "attach", "1", str(pic)); ok(rc == 0 and (TMP / "h" / "receipt_files" / "receipt1.png").exists(), "attach: " + o)
bad = TMP / "x.exe"; bad.write_bytes(b"MZ"); rc, o = jeeg("receipt", "attach", "1", str(bad)); ok(rc != 0, "exe refused")
rc, o = jeeg("receipt", "list", "2026-11"); ok("[file]" in o and "Big Bazaar" in o and "Market" not in o, "list: " + o)
rc, o = jeeg("receipt", "report", "2026"); ok(rc == 0 and (TMP / "receipts_2026.csv").exists() and "Shell" in (TMP / "receipts_2026.csv").read_text(), "report csv")
rc, o = jeeg("receipt", "remove", "2"); ok(rc == 0 and "Shell" not in jeeg("receipt", "list")[1], "remove")

# ---- setup check
rc, o = jeeg("setup", "check"); ok("Setup check" in o and "data folder is writable" in o, "setup check: " + o)
rc, o = jeeg("mqtt", "add", "ghost", "127.0.0.1:1"); rc, o = jeeg("setup", "check"); ok(rc != 0 and "MQTT broker 'ghost' answers" in o and "FIX" in o, "unreachable broker is reported: " + o)

# ---- setup home (fake HA + MQTT on this computer)
def listen(port, handler):
    s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try: s.bind(("127.0.0.1", port))
    except OSError: return None
    s.listen(5)
    def loop():
        while True:
            try: c, _ = s.accept()
            except OSError: return
            threading.Thread(target=lambda: (handler(c), c.close()), daemon=True).start()
    threading.Thread(target=loop, daemon=True).start(); return s
class HA(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self): self.send_response(401); self.end_headers()
hs = http.server.ThreadingHTTPServer(("127.0.0.1", 8123), HA) if not os.environ.get("NO_HA") else None
try:
    threading.Thread(target=hs.serve_forever, daemon=True).start()
    ha_ok = True
except Exception: ha_ok = False
ms = listen(1883, lambda c: None)
rc, o = jeeg("setup", "home", "127.0.0.1")
if ha_ok: ok("ha add home http://127.0.0.1:8123" in o, "finds Home Assistant: " + o)
if ms: ok("mqtt add home 127.0.0.1" in o, "finds MQTT: " + o)
ok("Nothing was saved" in o or "Nothing found" in o, "scan saves nothing")
rc, o = jeeg("setup", "home", "8.8.8.8"); ok(rc != 0, "public address refused")
rc, o = jeeg("setup", "home", "banana"); ok(rc != 0, "bad argument")

# ---- family board and backup share over the link
import jeeg_link as L, jeeg_chan as C
A, B = TMP / "A", TMP / "B"; A.mkdir(); B.mkdir()
L.Store(A).set_name("alpha"); L.Store(B).set_name("beta")
os.environ["HOME"] = os.environ["USERPROFILE"] = str(TMP / "rh"); (TMP / "rh").mkdir()
la = L.Listener(A, port=0, out=lambda s: None, interactive=True); ans = iter(["y", "chat"]); la.prompt = lambda t, default="": next(ans, default)
threading.Thread(target=la.serve, daemon=True).start(); la.ready.wait(5)
lb = L.Listener(B, port=0, out=lambda s: None, interactive=True); ans2 = iter(["y", "chat"]); lb.prompt = lambda t, default="": next(ans2, default)
threading.Thread(target=lb.serve, daemon=True).start(); lb.ready.wait(5)
try: L._cmd_pair(L.Store(B), [f"127.0.0.1:{la.port}"], True, lambda s: None, lambda p: "y" if "number" in p else "chat")
except Exception as ex: print("pair error", ex)
time.sleep(0.3)
d = L.Store(A).peers(); k = next(iter(d)); d[k]["addr"] = f"127.0.0.1:{lb.port}"; L.Store(A).save_peers(d)
d = L.Store(B).peers(); k = next(iter(d)); d[k]["addr"] = f"127.0.0.1:{la.port}"; L.Store(B).save_peers(d)
ea, eb = dict(env, JEEG_HOME=str(A), HOME=str(TMP / "rh")), dict(env, JEEG_HOME=str(B), HOME=str(TMP / "rh"))
rc, o = jeeg("board", "add", "buy milk", e=ea); ok(rc == 0 and "Only on this computer" in o, "board add (unshared): " + o)
rc, o = jeeg("channel", "share", "board", "with", "beta", e=ea); rc, o = jeeg("channel", "share", "board", "with", "alpha", e=eb)
rc, o = jeeg("board", "add", "call plumber", e=eb); ok(rc == 0 and "not delivered" not in o.lower(), "board add shared: " + o)
rc, o = jeeg("board", "list", e=ea); ok("call plumber" in o and "buy milk" in o, "alpha sees beta's item: " + o)
rc, ob = jeeg("board", "list", e=eb)
num = [l for l in ob.splitlines() if "call plumber" in l][0].split(".")[0].strip()
rc, o = jeeg("board", "done", num, e=eb); ok(rc == 0, "done: " + o)
time.sleep(0.5)
rc, o = jeeg("board", "list", e=ea); ok("call plumber" not in o.split("done:")[0] and "buy milk" in o, "done item disappears from alpha: " + o)
rc, o = jeeg("board", "done", "99", e=ea); ok(rc != 0, "bad number")
# backup share
(A / "expenses.csv").write_text("a,b\n1,2\n")
rc, o = jeeg("backup", "share", "beta", e=ea); ok(rc == 3, "backup share asks first: rc=%s %s" % (rc, o))
rc, o = jeeg("--yes", "backup", "share", "beta", e=ea); ok(rc == 0 and "Sent" in o, "backup share: " + o)
got = list((TMP / "rh" / "Downloads" / "JeeG received").glob("jeeg_backup_*.zip"))
ok(got and "expenses.csv" in zipfile.ZipFile(got[0]).namelist(), "backup arrived: " + str(got))
ok(not any("peers" in n or "psk" in n for n in zipfile.ZipFile(got[0]).namelist()), "link keys are not in the backup")
rc, o = jeeg("backup", "share", "nobody", e=ea); ok(rc != 0, "unknown computer")
# ---- bridge steps: sensor logging, notify, playbook
jeeg("playbook", "add", "hello", "=", "gst 100 18")
rc, o = jeeg("bridge", "add", "temp", "when", "udp", "40777", "then", "log reading temperature {msg} c ; notify Temperature {msg} ; playbook run hello"); ok(rc == 0, "bridge accepts log, notify, playbook steps: " + o)
rc, o = jeeg("bridge", "test", "temp", "24.5"); ok("log reading temperature 24.5 c  ->  ok" in o and "notify Temperature 24.5" in o and "playbook run hello  ->  ok" in o, "bridge test runs them: " + o)
rc, o = jeeg("show", "readings", "temperature"); ok("24.5" in o, "the reading was logged: " + o)
for bad in ("log tail x", "playbook add x = y", "playbook remove hello"):
    rc, o = jeeg("bridge", "add", "bad", "when", "udp", "40778", "then", bad); ok(rc != 0, "bridge refuses: " + bad)
print(f"extras: {P} passed, {F} failed"); sys.exit(1 if F else 0)
