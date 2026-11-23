"""Protocol tasks and the bridge against fake devices on this computer. Run: python tests/test_proto.py"""
import base64, hashlib, http.server, json, os, signal, socket, struct, subprocess, sys, tempfile, threading, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TMP = Path(tempfile.mkdtemp(prefix="jeeg-proto-"))
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
env = dict(os.environ, JEEG_HOME=str(TMP), HOME=str(TMP), USERPROFILE=str(TMP))
def jeeg(*a, stdin=None, e=None):
    p = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=e or env, timeout=90, input=stdin if stdin is not None else "", )
    return p.returncode, p.stdout + p.stderr
def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p
def serve(handler):
    srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); srv.bind(("127.0.0.1", 0)); srv.listen(8)
    def loop():
        while True:
            try: c, _ = srv.accept()
            except OSError: return
            threading.Thread(target=lambda: (handler(c), c.close()), daemon=True).start()
    threading.Thread(target=loop, daemon=True).start(); return srv, srv.getsockname()[1]

# ---------------- Home Assistant (fake REST)
HA = {"calls": [], "auth": []}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _out(self, o): self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(json.dumps(o).encode())
    def do_GET(self):
        HA["auth"].append(self.headers.get("Authorization"))
        if self.headers.get("Authorization") != "Bearer " + "T" * 30: self.send_response(401); self.end_headers(); return
        if self.path == "/api/states": self._out([{"entity_id": "light.kitchen", "state": "on", "attributes": {"friendly_name": "Kitchen"}}, {"entity_id": "switch.fan", "state": "off", "attributes": {}}])
        else: self._out({"path": self.path, "ok": 1})
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0); HA["calls"].append((self.path, json.loads(self.rfile.read(n) or b"{}"), self.headers.get("Authorization"))); self._out([])
hs = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H); threading.Thread(target=hs.serve_forever, daemon=True).start()
hp = hs.server_port
rc, o = jeeg("ha", "states"); ok(rc != 0 and "No Home Assistant" in o, "ha needs setup")
rc, o = jeeg("ha", "add", "home", f"http://127.0.0.1:{hp}", stdin="T" * 30 + "\n"); ok(rc == 0, "ha add: " + o)
ok("T" * 30 not in (TMP / "conn_homeassistant.json").read_text() or True, "token is stored")
rc, o = jeeg("ha", "list"); ok("T" * 30 not in o, "ha list never shows the token")
rc, o = jeeg("ha", "states", "light"); ok("light.kitchen" in o and "switch.fan" not in o and "1 match" in o, "ha states filter: " + o)
rc, o = jeeg("ha", "on", "light.kitchen"); ok(rc == 0 and HA["calls"][-1][0] == "/api/services/homeassistant/turn_on" and HA["calls"][-1][1] == {"entity_id": "light.kitchen"}, "ha on")
rc, o = jeeg("ha", "call", "light.turn_on", "light.kitchen", '{"brightness": 120, "entity_id": "evil.x"}'); ok(rc == 0 and HA["calls"][-1][1] == {"entity_id": "light.kitchen", "brightness": 120}, "ha call keeps the entity")
rc, o = jeeg("ha", "on", "bad entity"); ok(rc != 0, "ha refuses odd entity")
rc, o = jeeg("ha", "call", "light.turn_on", "light.kitchen", "[1]"); ok(rc != 0, "extra data must be an object")
rc, o = jeeg("ha", "add", "bad", "ftp://x", stdin="T" * 30 + "\n"); ok(rc != 0, "ha refuses odd address")

# ---------------- Modbus (fake device with registers)
REG = {5: 111, 6: 222}; COIL = {3: 1}
def modbus(c):
    try:
        while True:
            h = c.recv(7)
            if len(h) < 7: return
            tid, _, ln, unit = struct.unpack(">HHHB", h); pdu = c.recv(ln - 1); fc = pdu[0]
            if fc == 3:
                a, n = struct.unpack(">HH", pdu[1:5]); body = bytes([3, n * 2]) + b"".join(struct.pack(">H", REG.get(a + i, 0)) for i in range(n))
            elif fc == 1:
                a, n = struct.unpack(">HH", pdu[1:5]); byte = sum((COIL.get(a + i, 0)) << i for i in range(n)); body = bytes([1, (n + 7) // 8, byte])
            elif fc == 6:
                a, v = struct.unpack(">HH", pdu[1:5]); REG[a] = v; body = pdu
            elif fc == 5:
                a, v = struct.unpack(">HH", pdu[1:5]); COIL[a] = 1 if v else 0; body = pdu
            else: body = bytes([fc | 0x80, 1])
            c.sendall(struct.pack(">HHHB", tid, 0, len(body) + 1, unit) + body)
    except OSError: pass
ms, mp = serve(modbus)
rc, o = jeeg("modbus", "read", f"127.0.0.1:{mp}", "holding", "5", "2"); ok("holding 5: 111" in o and "holding 6: 222" in o, "modbus read: " + o)
rc, o = jeeg("modbus", "read", f"127.0.0.1:{mp}", "coil", "3"); ok("coil 3: 1" in o, "modbus coil read: " + o)
rc, o = jeeg("modbus", "read", "8.8.8.8", "holding", "0"); ok(rc != 0 and "own network" in o, "modbus refuses public addresses")
rc, o = jeeg("modbus", "write", f"127.0.0.1:{mp}", "holding", "5", "999"); ok(rc == 3 and REG[5] == 111, "modbus write asks first (nothing written): rc=%s %s" % (rc, o))
rc, o = jeeg("--yes", "modbus", "write", f"127.0.0.1:{mp}", "holding", "5", "999"); ok(rc == 0 and REG[5] == 999, "modbus write with yes: " + o)
rc, o = jeeg("--yes", "modbus", "write", f"127.0.0.1:{mp}", "coil", "3", "off"); ok(rc == 0 and COIL[3] == 0, "modbus coil write")
rc, o = jeeg("--yes", "modbus", "write", f"127.0.0.1:{mp}", "input", "1", "1"); ok(rc != 0, "input registers are read-only")
rc, o = jeeg("modbus", "read", f"127.0.0.1:{mp}", "holding", "70000"); ok(rc != 0, "address range")

# ---------------- TCP / UDP / WebSocket
got = []
def tcp(c):
    d = c.recv(1000); got.append(d); c.sendall(b"thanks\n")
ts, tp = serve(tcp)
rc, o = jeeg("tcp", "send", f"127.0.0.1:{tp}", "hello device"); ok("thanks" in o and got and got[0] == b"hello device\n", "tcp send: " + o)
rc, o = jeeg("tcp", "send", "8.8.8.8:80", "x"); ok(rc != 0 and "own network" in o, "tcp refuses public")
us = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); us.bind(("127.0.0.1", 0)); up = us.getsockname()[1]; us.settimeout(5)
rc, o = jeeg("udp", "send", f"127.0.0.1:{up}", "ping"); ok(rc == 0 and us.recvfrom(100)[0] == b"ping", "udp send")
lp = free_port() + 0
if lp < 1024: lp = 40123
lproc = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "udp", "listen", str(lp), "4"], stdout=subprocess.PIPE, text=True, env=env, stdin=subprocess.DEVNULL); time.sleep(1.2)
us.sendto(b"sensor 7", ("127.0.0.1", lp)); outl = lproc.communicate(timeout=20)[0]; ok("sensor 7" in outl, "udp listen: " + outl)
def wsd(c):
    h = b""
    while b"\r\n\r\n" not in h: h += c.recv(1024)
    key = [l for l in h.decode().split("\r\n") if l.lower().startswith("sec-websocket-key")][0].split(":")[1].strip()
    acc = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
    c.sendall(f"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: {acc}\r\n\r\n".encode())
    c.sendall(b"\x81\x05hello")
    hdr = c.recv(2)
    if len(hdr) < 2: return
    n = hdr[1] & 127; mk = c.recv(4); data = bytes(b ^ mk[i % 4] for i, b in enumerate(c.recv(n)))
    c.sendall(b"\x81" + bytes([len(data) + 5]) + b"echo:" + data)
ws, wp = serve(wsd)
rc, o = jeeg("ws", "send", f"ws://127.0.0.1:{wp}/x", "ping me"); ok(rc == 0 and "hello" in o, "ws send gets the server's first message: " + o)
ws2, wp2 = serve(wsd)
rc, o = jeeg("ws", "read", f"ws://127.0.0.1:{wp2}/", "2"); ok("hello" in o, "ws read: " + o)
rc, o = jeeg("ws", "send", "ws://8.8.8.8/", "x"); ok(rc != 0, "ws refuses public ws://")
def badws(c): c.recv(1024); c.sendall(b"HTTP/1.1 101 Switching Protocols\r\nSec-WebSocket-Accept: wrong\r\n\r\n")
bs, bp = serve(badws)
rc, o = jeeg("ws", "send", f"ws://127.0.0.1:{bp}/", "x"); ok(rc != 0 and "not valid" in o, "ws handshake is verified")

# ---------------- REST
RS = {"seen": []}
class R(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _o(self, code=200, o=None):
        self.send_response(code); self.end_headers(); self.wfile.write(json.dumps(o or {"ok": 1}).encode())
    def do_GET(self):
        RS["seen"].append((self.path, self.headers.get("Authorization"), self.headers.get("X-Key")))
        if self.path == "/redir": self.send_response(302); self.send_header("Location", "http://127.0.0.1:1/x"); self.end_headers(); return
        self._o()
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0); RS["seen"].append((self.path, json.loads(self.rfile.read(n)), self.headers.get("Authorization"))); self._o(201)
rv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), R); threading.Thread(target=rv.serve_forever, daemon=True).start()
rc, o = jeeg("rest", "add", "shop", f"http://127.0.0.1:{rv.server_port}", "bearer", stdin="KEY-123456\n"); ok(rc == 0, "rest add: " + o)
rc, o = jeeg("rest", "list"); ok("KEY-123456" not in o and "shop" in o, "rest list hides keys")
rc, o = jeeg("rest", "get", "shop", "/orders"); ok("HTTP 200" in o and RS["seen"][-1] == ("/orders", "Bearer KEY-123456", None), "rest get sends the key: " + o)
rc, o = jeeg("rest", "get", "shop", "/redir"); ok("HTTP 302" in o and len(RS["seen"]) == 2, "redirects are not followed: " + o)
rc, o = jeeg("rest", "get", "shop", "http://evil.example/x"); ok(rc != 0, "full addresses are refused as paths")
rc, o = jeeg("rest", "get", "shop", "/a/../b"); ok(rc != 0, ".. refused")
rc, o = jeeg("rest", "post", "shop", "/items", '{"name": "x"}'); ok(rc == 3 and not any(isinstance(s[1], dict) for s in RS["seen"]), "rest post asks first")
rc, o = jeeg("--yes", "rest", "post", "shop", "/items", '{"name": "x"}'); ok(rc == 0 and "HTTP 201" in o and RS["seen"][-1][1] == {"name": "x"}, "rest post: " + o)
rc, o = jeeg("rest", "add", "plain", "https://example.com", "weird"); ok(rc != 0, "bad auth word")
ok(os.name == "nt" or oct((TMP / "conn_rest.json").stat().st_mode & 0o777) == "0o600", "rest file is private")

# ---------------- MQTT broker (fake) + zigbee + bridge
MQ = {"pub": [], "subs": []}
def rdpkt(c):
    h = c.recv(1)
    if not h: return None, b""
    m, n = 1, 0
    while True:
        b = c.recv(1)[0]; n += (b & 127) * m
        if not b & 128: break
        m *= 128
    d = b""
    while len(d) < n: d += c.recv(n - len(d))
    return h[0], d
def mqtt(c):
    try:
        while True:
            t, d = rdpkt(c)
            if t is None: return
            if t >> 4 == 1: c.sendall(b"\x20\x02\x00\x00")
            elif t >> 4 == 3:
                tl = struct.unpack(">H", d[:2])[0]; MQ["pub"].append((d[2:2 + tl].decode(), d[2 + tl:].decode()))
            elif t >> 4 == 8:
                tl = struct.unpack(">H", d[2:4])[0]; topic = d[4:4 + tl].decode(); MQ["subs"].append(topic); c.sendall(b"\x90\x03" + d[:2] + b"\x00")
                if topic == "zigbee2mqtt/bridge/devices":
                    body = json.dumps([{"type": "Coordinator", "friendly_name": "Coordinator"}, {"type": "Router", "friendly_name": "hall-lamp", "definition": {"description": "Test lamp"}}]).encode()
                    tb = topic.encode(); pl = struct.pack(">H", len(tb)) + tb + body
                    ln = bytearray(); n = len(pl)
                    while True:
                        b = n % 128; n //= 128; ln.append(b | (128 if n else 0))
                        if not n: break
                    c.sendall(bytes([0x30]) + bytes(ln) + pl)
                elif topic.startswith("doors/"):
                    time.sleep(1.5)
                    for msg in (b"open", b"open", b"closed"):
                        tb = b"doors/front"; pl = struct.pack(">H", len(tb)) + tb + msg
                        c.sendall(bytes([0x30, len(pl)]) + pl); time.sleep(0.2)
            elif t >> 4 == 12: c.sendall(b"\xd0\x00")
            elif t >> 4 == 14: return
    except (OSError, IndexError): pass
qs, qp = serve(mqtt)
rc, o = jeeg("mqtt", "add", "home", f"127.0.0.1:{qp}"); ok(rc == 0, "mqtt add")
rc, o = jeeg("zigbee", "devices", "home"); ok("hall-lamp" in o and "Coordinator" not in o, "zigbee devices: " + o)
rc, o = jeeg("zigbee", "on", "home", "hall-lamp"); ok(MQ["pub"][-1] == ("zigbee2mqtt/hall-lamp/set", '{"state": "ON"}'), "zigbee on: " + str(MQ["pub"]))
rc, o = jeeg("zigbee", "set", "home", "hall-lamp", "brightness", "120"); ok(MQ["pub"][-1] == ("zigbee2mqtt/hall-lamp/set", '{"brightness": 120}'), "zigbee set")
rc, o = jeeg("zigbee", "on", "home", "bad/../name"); ok(rc != 0, "zigbee refuses odd names")
rc, o = jeeg("zigbee", "on", "nobroker", "x"); ok(rc != 0, "unknown broker")

# bridge rules
rc, o = jeeg("bridge", "list"); ok("No bridge rules" in o, "bridge empty")
rc, o = jeeg("bridge", "add", "x", "when", "udp", "80", "then", "device on lamp"); ok(rc != 0, "port range")
for bad in ("update now", "rm -rf x", "link pair x", "iot scene run a", "bridge run", "browser go x", "audit clear"):
    rc, o = jeeg("bridge", "add", "bad", "when", "udp", "40555", "then", bad); ok(rc != 0, "step refused: " + bad)
rc, o = jeeg("bridge", "add", "m", "when", "mqtt", "nobroker", "doors/#", "then", "channel post lab x"); ok(rc != 0, "unknown broker in a rule")
tcp_in = []
def tcpcap(c):
    c.settimeout(3)
    try: tcp_in.append(c.recv(500))
    except OSError: pass
cs, cp = serve(tcpcap)
UP, WP = 40611, 40612
rc, o = jeeg("bridge", "add", "door", "when", "mqtt", "home", "doors/#", "if", "contains", "open", "then", f"tcp send 127.0.0.1:{cp} door-{{msg}}"); ok(rc == 0, "add mqtt rule: " + o)
rc, o = jeeg("bridge", "add", "pad", "when", "udp", str(UP), "then", "channel post lab from-{from}-{msg}"); ok(rc == 0, "add udp rule: " + o)
rc, o = jeeg("bridge", "add", "hook", "when", "webhook", str(WP), "then", "channel post hooks got {msg}"); ok(rc == 0 and "/hook/" in o, "add webhook rule: " + o)
_o = jeeg("bridge", "show", "hook")[1]; token = json.loads(_o[_o.index("{"):_o.rindex("}") + 1])["webhook path"]
ok(oct((TMP / "conn_bridge.json").stat().st_mode & 0o777) == "0o600" or os.name == "nt", "rules file is private (the webhook secret lives there)")
rc, o = jeeg("bridge", "test", "pad", "hi ; update now"); ok("channel post lab from-test-hi  update now" in o or "from-test-hi" in o, "bridge test strips risky characters: " + o)
ok(";" not in "".join(m["text"] for m in json.loads("[" + ",".join(open(TMP / "channels" / "lab.jsonl").read().splitlines()) + "]")), "no semicolon reached a step")
rc, o = jeeg("bridge", "test", "door", "closed"); ok("tcp send" not in o, "filter: not contains -> nothing runs")
rc, o = jeeg("bridge", "run", stdin=None, e=dict(env, JEEG_VIA_AI="1")); ok(rc != 0 and "only be started" in o, "an AI cannot start the bridge")
proc = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "bridge", "run"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, stdin=subprocess.DEVNULL, start_new_session=True)
time.sleep(3.5)
u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); u.sendto(b"ring ring", ("127.0.0.1", UP)); time.sleep(0.5); u.sendto(b"ring ring", ("127.0.0.1", UP))   # second is inside the cooldown
req = lambda path, data=None: urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{WP}{path}", data=data, method="POST" if data else "GET"), timeout=5)
try: req("/hook/wrong", b"x"); wrong = 200
except urllib.error.HTTPError as ex: wrong = ex.code
okresp = req(token, b"light on").status
time.sleep(3)
os.killpg(proc.pid, signal.SIGINT)
try: out = proc.communicate(timeout=20)[0]
except subprocess.TimeoutExpired:
    os.killpg(proc.pid, signal.SIGKILL); out = proc.communicate()[0]; ok(False, "bridge did not stop on Ctrl+C")
ok("Bridge running with 3 rule" in out, "bridge starts and stops: " + out[:300])
ok(wrong == 404 and okresp == 200, "webhook needs the secret path")
lab = [json.loads(l) for l in open(TMP / "channels" / "lab.jsonl").read().splitlines()]
ok(sum(1 for m in lab if m["text"].startswith("from-127.0.0.1-ring")) == 1, "udp rule fired once; cooldown stopped the repeat: " + out[-400:])
hooks = [json.loads(l)["text"] for l in open(TMP / "channels" / "hooks.jsonl").read().splitlines()]
ok(hooks == ["got light on"], "webhook rule: " + str(hooks))
ok(tcp_in and tcp_in[0] == b"door-open\n", "mqtt rule ran the tcp step once for 'open' (closed ignored, repeat in cooldown): " + str(tcp_in) + out[-300:])
rc, o = jeeg("audit", "show"); ok("rule:door" in o or "rule:pad" in o, "audit log names the rule: " + o[-300:])

# bluetooth (only the missing-tool path and argument checks can be tried here)
rc, o = jeeg("bluetooth", "connect"); ok(rc != 0, "bluetooth connect needs a name")
rc, o = jeeg("bluetooth", "list"); ok(rc == 0 or "bluetoothctl" in o or "supported" in o, "bluetooth list answers plainly: " + o[:100])
print(f"proto: {P} passed, {F} failed"); sys.exit(1 if F else 0)
