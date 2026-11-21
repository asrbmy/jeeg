"""IoT hub scenes against a fake Shelly on this computer. Run: python tests/test_iot.py"""
import http.server, json, os, subprocess, sys, tempfile, threading
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TMP = Path(tempfile.mkdtemp(prefix="jeeg-iot-"))
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
HITS = []
STATE = {"on": True}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        HITS.append(self.path)
        if "Switch.Set" in self.path: STATE["on"] = "on=true" in self.path
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps({"output": STATE["on"]}).encode())
srv = http.server.HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
env = dict(os.environ, JEEG_HOME=str(TMP))
def run(*a):
    p = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=env, timeout=90, stdin=subprocess.DEVNULL)
    return p.returncode, p.stdout + p.stderr
rc, o = run("iot", "list"); ok(rc == 0 and "Nothing saved" in o, "empty list")
rc, o = run("device", "add", "lamp", "shelly", f"127.0.0.1:{srv.server_port}"); ok(rc == 0, "device add: " + o)
rc, o = run("iot", "scene", "add", "night", "=", "device off lamp ; pause 1 ; device status lamp"); ok(rc == 0 and "3 steps" in o, "scene add")
rc, o = run("iot", "list"); ok("lamp" in o and "night" in o, "list shows devices and scenes")
rc, o = run("iot", "scene", "run", "night")
ok(rc == 0 and "done" in o and STATE["on"] is False, "scene turned the lamp off: " + o)
ok(any("Switch.Set" in h for h in HITS), "the device was called")
for bad in ("rm -rf x", "update", "link pair x", "link level x full", "pause 999", "iot scene run night", "browser go x", "audit clear"):
    rc, o = run("iot", "scene", "add", "bad", "=", bad); ok(rc != 0, "refused step: " + bad)
rc, o = run("iot", "scene", "add", "x", "="); ok(rc != 0, "needs steps")
rc, o = run("iot", "scene", "add", "big", "=", " ; ".join(["device status lamp"] * 25)); ok(rc != 0, "too many steps")
# a hand-edited scene file cannot smuggle in other tasks
f = TMP / "conn_scenes.json"; d = json.loads(f.read_text()); d["evil"] = ["update apps"]; f.write_text(json.dumps(d))
rc, o = run("iot", "scene", "run", "evil"); ok(rc != 0 and "can be" in o, "edited scene file checked at run time")
rc, o = run("iot", "scene", "remove", "night"); ok(rc == 0, "remove")
rc, o = run("iot", "scene", "run", "night"); ok(rc != 0, "gone")
print(f"iot: {P} passed, {F} failed"); sys.exit(1 if F else 0)
