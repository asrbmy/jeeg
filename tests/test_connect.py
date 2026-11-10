"""Connectors: Telegram bot, hooks, webhooks, devices, MQTT, mail, GitHub, calendar feeds, ssh, adb, peers, MCP client.
Everything runs against fake servers on this computer; nothing touches the internet."""
import http.server, json, os, re, socket, stat, struct, subprocess, sys, tempfile, threading, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
HOME = tempfile.mkdtemp(prefix="jeeg-cn-"); WORK = Path(tempfile.mkdtemp(prefix="jeeg-cn-w-"))
BIN = Path(tempfile.mkdtemp(prefix="jeeg-cn-bin-"))
ENV = dict(os.environ, JEEG_HOME=HOME, PYTHONIOENCODING="utf-8", PATH=str(BIN) + os.pathsep + os.environ["PATH"])
P = F = 0
def ok(c, label):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", label)
def jeeg(*words, stdin="", env=None, timeout=90, yes=False):
    a = [sys.executable, str(ROOT / "jeeg.py")] + (["--yes"] if yes else []) + list(words)
    r = subprocess.run(a, capture_output=True, text=True, env=env or ENV, cwd=WORK, input=stdin, timeout=timeout)
    return r.returncode, r.stdout + r.stderr
def server(handler_cls):
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, s.server_address[1]
def fake_bin(name, body):
    p = BIN / name; p.write_text("#!/bin/sh\n" + body); p.chmod(p.stat().st_mode | stat.S_IEXEC)
def mode(p): return oct(os.stat(p).st_mode)[-3:]

# =========================================================== Telegram
TOKEN = "123456789:AAFakeTokenForTestsOnly_abcdefghijklmnopq"
tg = {"queue": [], "sent": [], "lock": threading.Lock(), "next": 1}
class TG(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        n = int(self.headers.get("Content-Length", "0")); body = json.loads(self.rfile.read(n) or b"{}")
        m = self.path.rsplit("/", 1)[-1]
        if not self.path.startswith(f"/bot{TOKEN}/"): out = {"ok": False, "description": "bad token"}
        elif m == "getMe": out = {"ok": True, "result": {"username": "jeeg_test_bot"}}
        elif m == "sendMessage":
            with tg["lock"]: tg["sent"].append((body.get("chat_id"), body.get("text")))
            out = {"ok": True, "result": {}}
        elif m == "getUpdates":
            off = body.get("offset", 0); res = []
            for _ in range(15):
                with tg["lock"]: res = [u for u in tg["queue"] if u["update_id"] >= off]
                if res: break
                time.sleep(0.1)
            out = {"ok": True, "result": res}
        else: out = {"ok": False}
        data = json.dumps(out).encode(); self.send_response(200); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
tgs, tgport = server(TG)
def push(chat, text, ctype="private"):
    with tg["lock"]:
        tg["queue"].append({"update_id": tg["next"], "message": {"chat": {"id": chat, "type": ctype}, "text": text}}); tg["next"] += 1
def replies(chat): 
    with tg["lock"]: return [t for c, t in tg["sent"] if c == chat]
def wait_reply(chat, n, secs=20):
    for _ in range(int(secs * 10)):
        if len(replies(chat)) >= n: return True
        time.sleep(0.1)
    return False
tenv = dict(ENV, JEEG_TELEGRAM_API=f"http://127.0.0.1:{tgport}")
rc, out = jeeg("telegram", "setup", stdin="not-a-token\n", env=tenv); ok(rc == 1 and "does not look like" in out, "bad token refused")
rc, out = jeeg("telegram", "setup", stdin=TOKEN + "\n", env=tenv)
ok(rc == 0 and "@jeeg_test_bot" in out and TOKEN not in out, "setup accepted and token not echoed: " + out[:150])
ok(mode(Path(HOME) / "telegram.json") == "600" or os.name == "nt", "token file is private")
# a foreign API address is ignored (the token must never leave for another host)
import importlib; sys.path.insert(0, str(ROOT)); os.environ["JEEG_HOME"] = HOME
import jeeg_connect as C
os.environ["JEEG_TELEGRAM_API"] = "http://evil.example"; ok(C.api_base() == C.DEFAULT_API, "foreign API address ignored")
os.environ["JEEG_TELEGRAM_API"] = "https://127.0.0.1:1"; ok(C.api_base() == C.DEFAULT_API, "https override ignored"); del os.environ["JEEG_TELEGRAM_API"]
proc = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "telegram start safe limit 3"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=tenv, cwd=WORK, stdin=subprocess.DEVNULL)
head = ""
for _ in range(60):
    ln = proc.stdout.readline(); head += ln
    if "Every call is printed" in ln or not ln: break
m = re.search(r"/pair (\d{6})", head); code = m.group(1) if m else "000000"
ok(m is not None and TOKEN not in head, "pairing code shown, token not shown: " + head[:200])
push(111, "gst 100 18"); ok(wait_reply(111, 1) and "private" in replies(111)[0], "unpaired chat is refused")
ok(all("118" not in t for t in replies(111)), "unpaired chat gets no task output")
push(111, "/pair 000000"); wait_reply(111, 2)
push(222, "hello", "group"); push(222, "/pair " + code, "supergroup"); time.sleep(1.5); ok(replies(222) == [], "group chats are ignored")
push(111, "/pair " + code); ok(wait_reply(111, 3) and "Paired" in replies(111)[-1], "right code pairs")
ok(json.loads((Path(HOME) / "telegram.json").read_text())["allowed"] == [111], "pairing is saved")
push(111, "gst 100 18"); ok(wait_reply(111, 4) and "118" in replies(111)[-1], "paired chat runs a task: " + str(replies(111)[-1:]))
push(111, "open youtube"); ok(wait_reply(111, 5) and ("not allowed" in replies(111)[-1] or "Failed" in replies(111)[-1]), "safe mode refuses other tasks")
push(111, "/mode"); ok(wait_reply(111, 6) and "safe" in replies(111)[-1].lower(), "/mode")
push(111, "web god"); wait_reply(111, 7); ok("terminal" in replies(111)[-1], "terminal-only commands refused")
push(111, "gst 5 18"); ok(wait_reply(111, 8) and "limit" in replies(111)[-1], "request limit applies (3)")
push(111, "/stop"); ok(wait_reply(111, 9), "stop answered")
try: proc.wait(20)
except subprocess.TimeoutExpired: proc.kill()
out_rest = proc.stdout.read(); ok(proc.returncode == 0, "bot exits cleanly on /stop"); ok(TOKEN not in head + out_rest, "token never printed")
logs = sorted((Path(HOME) / "ai-sessions").glob("*.log")); ok(logs and TOKEN not in logs[-1].read_text(), "token not in the session log")
# a wrong pairing code 5 times locks pairing
with tg["lock"]: tg["queue"].clear(); tg["sent"].clear()
st = {"log": lambda *_: None, "allowed": [], "code": "123456", "pair_bad": 0, "state": HOME, "mode": "safe", "approver": None, "extra": (), "limit": 0, "calls": 0}
class Rec:
    token = TOKEN
    def __init__(s): s.sent = []
    def send(s, cid, text): s.sent.append(text)
r = Rec()
for _ in range(7): C.handle_message(r, {"chat": {"id": 5, "type": "private"}, "text": "/pair 999999"}, st)
C.handle_message(r, {"chat": {"id": 5, "type": "private"}, "text": "/pair 123456"}, st)
ok(st["allowed"] == [] and len(r.sent) == 5, "pairing locks after 5 wrong codes, even for the right code")
rc, out = jeeg("telegram", "forget", env=tenv); ok(rc == 0 and not (Path(HOME) / "telegram.json").exists(), "forget deletes the token")
tgs.shutdown()

# =========================================================== hooks
rc, out = jeeg("hook", "add", "bad", "=", "web god"); ok(rc == 1, "hook cannot run terminal commands")
rc, out = jeeg("hook", "add", "bad", "=", "gst 1 1 then gst 2 2"); ok(rc == 1, "hook cannot chain")
rc, out = jeeg("hook", "add", "tax", "=", "gst 100 18"); ok(rc == 0 and "gst_amount" in out, "hook add")
rc, out = jeeg("hook", "add", "down", "=", "shutdown in 60 minutes"); ok(rc == 0, "hook add confirm task")
rc, out = jeeg("hook", "list"); ok("tax" in out and "gst 100 18" in out, "hook list")
hp = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "hook listen no tunnel"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=ENV, cwd=WORK, stdin=subprocess.DEVNULL)
head = ""
for _ in range(40):
    ln = hp.stdout.readline(); head += ln
    if "Every call is printed" in ln or not ln: break
lm = re.search(r"(http://127\.0\.0\.1:(\d+)/(\S+?)/)tax", head); ok(lm is not None, "hook link printed: " + head[:200])
def hit(url, method="GET", data=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method=method), timeout=30) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, (json.loads(e.read() or b"{}") if e.headers.get("Content-Type", "").startswith("application/json") else {})
if lm:
    base = lm.group(1)
    c, d = hit(base + "tax"); ok(c == 200 and d["ok"] and "118" in d["output"], "hook runs its saved task")
    c, d = hit(base + "tax", "POST", b'{"query": "hash text evil"}'); ok(c == 200 and "evil" not in d["output"].lower() and "118" in d["output"], "caller cannot change the task")
    c, d = hit(base + "down"); ok(c == 200 and d["ok"] is False and "confirmation" in d["output"], "confirmation tasks are refused from hooks")
    ok(hit(base + "nope")[0] == 404, "unknown hook 404")
    ok(hit(f"http://127.0.0.1:{lm.group(2)}/wrong/tax")[0] == 404, "wrong secret 404")
    ok(hit(base[:-1] + "x/tax")[0] == 404, "almost-right secret 404")
    for _ in range(14): code, _d = hit(base + "tax")
    ok(code == 429, "hooks are rate limited")
hp.terminate(); hp.wait(5)
rc, out = jeeg("hook", "remove", "tax"); ok(rc == 0, "hook remove")

# =========================================================== webhook
got = []
class WH(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        got.append((self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
        self.send_response(200); self.send_header("Content-Length", "2"); self.end_headers(); self.wfile.write(b"ok")
whs, whport = server(WH)
rc, out = jeeg("webhook", "add", "team", f"http://127.0.0.1:{whport}/services/SECRETPATH"); ok(rc == 0, "webhook add (local http allowed)")
rc, out = jeeg("webhook", "list"); ok("team" in out and "SECRETPATH" not in out, "webhook list hides the secret path: " + out)
ok(mode(Path(HOME) / "conn_webhooks.json") == "600" or os.name == "nt", "webhook file is private")
rc, out = jeeg("webhook", "send", "team", "deploy done ✓", yes=True); ok(rc == 0 and got and got[0][0] == "/services/SECRETPATH" and got[0][1]["text"] == "deploy done ✓" and got[0][1]["content"] == "deploy done ✓", "webhook send posts text+content")
for bad in ("http://example.com/x", "ftp://x.com/y", "https://user:pw@x.com/z", "javascript:alert(1)", "https://"):
    rc, out = jeeg("webhook", "add", "x", bad); ok(rc == 1, "webhook refuses " + bad)
rc, out = jeeg("webhook", "add", "Bad Name!", "https://x.example.com/h"); ok(rc == 1, "webhook name validated")
rc, out = jeeg("webhook", "remove", "team"); ok(rc == 0, "webhook remove")
whs.shutdown()

# =========================================================== wake on LAN
rc, out = jeeg("wake", "add", "nas", "AA:BB:CC:DD:EE:FF"); ok(rc == 0, "wake add")
rc, out = jeeg("wake", "add", "bad", "AA:BB:CC"); ok(rc == 1, "bad MAC refused")
rc, out = jeeg("wake", "list"); ok("AA:BB:CC:DD:EE:FF" in out, "wake list")
rc, out = jeeg("wake", "nas"); ok((rc == 0 and "packet sent" in out) or "Could not send" in out, "wake sends (or says the network is missing): " + out[:100])
rc, out = jeeg("wake", "nobody"); ok(rc == 1, "unknown wake name")

# =========================================================== ssh computers
rc, out = jeeg("computer", "add", "pi", "pi@192.168.1.20"); ok(rc == 0, "computer add")
for bad in ("-oProxyCommand=touch", "pi@host name", "$(id)", "a;b"):
    rc, out = jeeg("computer", "add", "x", bad); ok(rc == 1, "computer refuses " + bad)
rc, out = jeeg("computer", "list"); ok("pi@192.168.1.20" in out, "computer list")
fake_bin("ssh", 'echo "ARGS: $@"; echo "disk fine"')
rc, out = jeeg("on", "pi", "run", "disk space; rm -rf /", yes=True)
ok(rc == 0 and "BatchMode=yes" in out and " -- pi@192.168.1.20 " in out and "jeeg 'disk space; rm -rf /'" in out, "ssh gets -- and a quoted task: " + out[:250])
rc, out = jeeg("on", "ghost", "run", "disk space", yes=True); ok(rc == 1 and "No saved computer" in out, "unknown computer")
fake_bin("ssh", "exit 255")
rc, out = jeeg("on", "pi", "run", "disk space", yes=True); ok(rc == 1 and "Could not connect" in out, "ssh failure explained")

# =========================================================== smart devices (Shelly Gen2, Gen1, Tasmota)
state = {"gen2": False, "gen1": False, "tas": False}
class Dev(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        p = self.path; body = None
        if p.startswith("/rpc/Switch.GetStatus"): body = {"output": state["gen2"]} if self.server.kind == "gen2" else None
        elif p.startswith("/rpc/Switch.Set"): state["gen2"] = "on=true" in p; body = {}
        elif p.startswith("/rpc/Switch.Toggle"): state["gen2"] = not state["gen2"]; body = {}
        elif p.startswith("/relay/0?turn="): state["gen1"] = p.endswith("on") or (not p.endswith("off") and not state["gen1"]); body = {}
        elif p == "/relay/0": body = {"ison": state["gen1"]}
        elif p.startswith("/cm?cmnd="):
            c = p.split("=", 1)[1]
            if "On" in c: state["tas"] = True
            elif "Off" in c: state["tas"] = False
            elif "Toggle" in c: state["tas"] = not state["tas"]
            body = {"POWER": "ON" if state["tas"] else "OFF"}
        if body is None: self.send_response(404); self.send_header("Content-Length", "0"); self.end_headers(); return
        d = json.dumps(body).encode(); self.send_response(200); self.send_header("Content-Length", str(len(d))); self.end_headers(); self.wfile.write(d)
def dev_server(kind):
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Dev); s.kind = kind
    threading.Thread(target=s.serve_forever, daemon=True).start(); return s, s.server_address[1]
d2, p2 = dev_server("gen2"); d1, p1 = dev_server("gen1")
rc, out = jeeg("device", "add", "lamp", "shelly", f"127.0.0.1"); ok(rc == 0, "device add")
# the saved address has no port, so write ports directly for the fake servers
reg = json.loads((Path(HOME) / "conn_devices.json").read_text())
reg["lamp"]["ip"] = f"127.0.0.1:{p2}"; reg["old"] = {"kind": "shelly", "ip": f"127.0.0.1:{p1}"}; reg["plug"] = {"kind": "tasmota", "ip": f"127.0.0.1:{p1}"}
(Path(HOME) / "conn_devices.json").write_text(json.dumps(reg))
rc, out = jeeg("device", "on", "lamp"); ok("ON" in out and state["gen2"], "shelly gen2 on: " + out)
rc, out = jeeg("device", "off", "lamp"); ok("OFF" in out and not state["gen2"], "shelly gen2 off")
rc, out = jeeg("device", "toggle", "lamp"); ok("ON" in out, "shelly gen2 toggle")
rc, out = jeeg("device", "on", "old"); ok("ON" in out, "shelly gen1 on: " + out)
rc, out = jeeg("device", "status", "old"); ok("ON" in out, "shelly gen1 status")
rc, out = jeeg("device", "on", "plug"); ok("ON" in out and state["tas"], "tasmota on: " + out)
rc, out = jeeg("device", "off", "plug"); ok("OFF" in out, "tasmota off")
rc, out = jeeg("device", "add", "far", "shelly", "8.8.8.8"); ok(rc == 1 and "own network" in out, "public device address refused")
rc, out = jeeg("device", "add", "far", "hue", "192.168.1.5"); ok(rc == 1, "unknown device kind refused")
rc, out = jeeg("device", "list"); ok("lamp" in out, "device list")
d1.shutdown(); d2.shutdown()

# =========================================================== MQTT
mq = {"pub": [], "conn": []}
def broker(port_holder):
    srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(5); port_holder.append(srv.getsockname()[1])
    def read_packet(c):
        h = c.recv(1)
        if not h: return None, b""
        mult, n = 1, 0
        while True:
            b = c.recv(1)[0]; n += (b & 127) * mult
            if not b & 128: break
            mult *= 128
        data = b""
        while len(data) < n: data += c.recv(n - len(data))
        return h[0], data
    def serve1(c):
        try:
            while True:
                t, data = read_packet(c)
                if t is None: return
                if t >> 4 == 1:
                    mq["conn"].append(data); c.sendall(b"\x20\x02\x00\x00")
                elif t >> 4 == 3:
                    tl = struct.unpack(">H", data[:2])[0]; mq["pub"].append((data[2:2 + tl].decode(), data[2 + tl:].decode()))
                elif t >> 4 == 8:
                    c.sendall(b"\x90\x03" + data[:2] + b"\x00")
                    topic = b"sensors/temp"; payload = b"21.5"; body = struct.pack(">H", len(topic)) + topic + payload
                    c.sendall(bytes([0x30, len(body)]) + body)
                elif t >> 4 == 14: return
        except (OSError, IndexError): pass
        finally: c.close()
    def loop():
        while True:
            try: c, _ = srv.accept()
            except OSError: return
            threading.Thread(target=serve1, args=(c,), daemon=True).start()
    threading.Thread(target=loop, daemon=True).start(); return srv
ph = []; bsrv = broker(ph)
rc, out = jeeg("mqtt", "add", "home", f"127.0.0.1:{ph[0]}"); ok(rc == 0, "mqtt add")
rc, out = jeeg("mqtt", "publish", "home", "lights/kitchen", "on now"); ok(rc == 0 and mq["pub"] == [("lights/kitchen", "on now")], "mqtt publish: " + out + str(mq["pub"]))
rc, out = jeeg("mqtt", "publish", "home", "lights/#", "x"); ok(rc == 1, "publish to a wildcard refused")
rc, out = jeeg("mqtt", "listen", "home", "sensors/#", "3"); ok("sensors/temp: 21.5" in out, "mqtt listen: " + out)
rc, out = jeeg("mqtt", "add", "secure", f"127.0.0.1:{ph[0]}", "bob", stdin="s3cretPW\n"); ok(rc == 0, "mqtt add with user")
rc, out = jeeg("mqtt", "list"); ok("secure" in out and "s3cretPW" not in out, "mqtt list never shows the password")
rc, out = jeeg("mqtt", "publish", "secure", "a/b", "hi"); ok(rc == 0 and any(b"bob" in c and b"s3cretPW" in c for c in mq["conn"]), "mqtt sends the user and password")
ok(mode(Path(HOME) / "conn_mqtt.json") == "600" or os.name == "nt", "mqtt file is private")
bsrv.close()

# =========================================================== mail (fake IMAP + SMTP on this computer)
mailbox = {"sent": [], "logins": []}
def line_server(handler):
    srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen(5)
    def loop():
        while True:
            try: c, _ = srv.accept()
            except OSError: return
            threading.Thread(target=handler, args=(c,), daemon=True).start()
    threading.Thread(target=loop, daemon=True).start(); return srv, srv.getsockname()[1]
def smtp(c):
    f = c.makefile("rwb", buffering=0)
    f.write(b"220 fake\r\n")
    data_mode = False; buf = []
    for raw in f:
        l = raw.decode().rstrip("\r\n")
        if data_mode:
            if l == ".": mailbox["sent"].append("\n".join(buf)); f.write(b"250 queued\r\n"); data_mode = False; buf = []
            else: buf.append(l)
            continue
        u = l.upper()
        if u.startswith("EHLO") or u.startswith("HELO"): f.write(b"250-fake\r\n250 AUTH PLAIN LOGIN\r\n")
        elif u.startswith("AUTH PLAIN"): mailbox["logins"].append(l); f.write(b"235 ok\r\n")
        elif u.startswith("AUTH LOGIN"): f.write(b"334 VXNlcm5hbWU6\r\n"); user = f.readline(); f.write(b"334 UGFzc3dvcmQ6\r\n"); pw = f.readline(); mailbox["logins"].append((user, pw)); f.write(b"235 ok\r\n")
        elif u.startswith(("MAIL", "RCPT")): f.write(b"250 ok\r\n")
        elif u == "DATA": f.write(b"354 go\r\n"); data_mode = True
        elif u == "QUIT": f.write(b"221 bye\r\n"); break
        else: f.write(b"250 ok\r\n")
    c.close()
def imap(c):
    f = c.makefile("rwb", buffering=0); f.write(b"* OK fake\r\n")
    for raw in f:
        tag, _, cmd = raw.decode().rstrip("\r\n").partition(" "); u = cmd.upper()
        if u.startswith("CAPABILITY"): f.write(b"* CAPABILITY IMAP4rev1\r\n" + tag.encode() + b" OK done\r\n")
        elif u.startswith("LOGIN"): mailbox["logins"].append(cmd); f.write(tag.encode() + b" OK logged in\r\n")
        elif u.startswith("SELECT") or u.startswith("EXAMINE"): f.write(b"* 2 EXISTS\r\n" + tag.encode() + b" OK [READ-ONLY] done\r\n")
        elif u.startswith("SEARCH"): f.write(b"* SEARCH 1 2\r\n" + tag.encode() + b" OK done\r\n")
        elif u.startswith("FETCH"):
            n = cmd.split()[1]; hdr = f"From: Alice {n} <a{n}@example.com>\r\nSubject: Hello number {n}\r\nDate: Mon, 9 Nov 2026 10:00:00 +0000\r\n\r\n".encode()
            f.write(b"* " + n.encode() + b" FETCH (BODY[HEADER.FIELDS (FROM SUBJECT DATE)] {" + str(len(hdr)).encode() + b"}\r\n" + hdr + b")\r\n" + tag.encode() + b" OK done\r\n")
        elif u.startswith("LOGOUT"): f.write(b"* BYE\r\n" + tag.encode() + b" OK bye\r\n"); break
        else: f.write(tag.encode() + b" OK\r\n")
    c.close()
ss, sp = line_server(smtp); is_, ip = line_server(imap)
rc, out = jeeg("mail", "status"); ok("No mail account" in out, "mail status when empty")
rc, out = jeeg("mail", "setup", "me@example.com", "not a host", "x.y"); ok(rc == 1, "mail setup validates hosts")
rc, out = jeeg("mail", "setup", "me@example.com", f"127.0.0.1:{ip}", f"127.0.0.1:{sp}", stdin="app-password-123\n")
ok(rc == 0 and "app-password-123" not in out, "mail setup saved without echoing the password: " + out[:120])
ok(mode(Path(HOME) / "conn_mail.json") == "600" or os.name == "nt", "mail file is private")
rc, out = jeeg("mail", "status"); ok("me@example.com" in out and "app-password-123" not in out, "mail status hides the password")
rc, out = jeeg("mail", "inbox"); ok(rc == 0 and "2 unread" in out and "Hello number 2" in out and "Alice 1" in out, "mail inbox lists unread: " + out)
ok(any("app-password-123" in str(x) for x in mailbox["logins"]), "inbox logged in with the saved password")
rc, out = jeeg("mail", "send", "bob@example.com", "|", "Hi there", "|", "Body line", yes=True); ok(rc == 0 and "Sent to bob@example.com" in out and mailbox["sent"] and "Subject: Hi there" in mailbox["sent"][0], "mail send: " + out)
rc, out = jeeg("mail", "send", "bob@example.com | " + "S" * 250 + " | body", yes=True); ok(rc == 1, "mail send rejects a very long subject")
rc, out = jeeg("mail", "send", "bob@example.com,eve@example.com | s | b", yes=True); ok(rc == 1, "mail send takes exactly one recipient")
rc, out = jeeg("mail", "send", "bob@example.com | s | b"); ok(rc == 3 or "confirm" in out.lower() or "Sent" not in out, "mail send asks for confirmation without --yes: " + out[:80])
rc, out = jeeg("mail", "forget"); ok(rc == 0, "mail forget"); rc, out = jeeg("mail", "inbox"); ok(rc == 1 and "No mail account" in out, "mail needs an account")
ss.close(); is_.close()

# =========================================================== GitHub (fake API)
class GH(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        auth = self.headers.get("Authorization", "")
        if self.path.startswith("/notifications"):
            body = [{"repository": {"full_name": "me/app"}, "subject": {"type": "PullRequest", "title": "Fix the thing"}}] if auth == "Bearer ghp_FakeTokenFakeTokenFake1234" else None
        elif self.path.startswith("/repos/me/app/issues"):
            body = [{"number": 7, "title": "Crash on start", "user": {"login": "ann"}}, {"number": 8, "title": "A PR", "user": {"login": "bo"}, "pull_request": {}}]
        else: body = None
        code = 200 if body is not None else 401
        d = json.dumps(body if body is not None else {}).encode(); self.send_response(code); self.send_header("Content-Length", str(len(d))); self.end_headers(); self.wfile.write(d)
ghs, ghp = server(GH); genv = dict(ENV, JEEG_GITHUB_API=f"http://127.0.0.1:{ghp}")
rc, out = jeeg("github", "login", stdin="short\n", env=genv); ok(rc == 1, "github rejects a malformed token")
rc, out = jeeg("github", "login", stdin="ghp_FakeTokenFakeTokenFake1234\n", env=genv); ok(rc == 0 and "ghp_" not in out, "github login saved privately")
ok(mode(Path(HOME) / "conn_github.json") == "600" or os.name == "nt", "github file is private")
rc, out = jeeg("github", "inbox", env=genv); ok("me/app" in out and "Fix the thing" in out, "github inbox: " + out)
rc, out = jeeg("github", "issues", "me/app", env=genv); ok("#7" in out and "#8" not in out, "github issues excludes pull requests")
rc, out = jeeg("github", "prs", "me/app", env=genv); ok("#8" in out and "#7" not in out, "github prs")
rc, out = jeeg("github", "issues", "../etc/passwd", env=genv); ok(rc == 1, "github repo name validated")
ghs.shutdown()
# the token never goes to a non-local API override
rc, out = jeeg("github", "inbox", env=dict(ENV, JEEG_GITHUB_API="http://evil.example")); ok("evil.example" not in out, "github ignores a foreign API override")
jeeg("github", "forget")

# =========================================================== calendar feed
import datetime as dt
d0 = dt.datetime.now() + dt.timedelta(days=1); d1 = dt.datetime.now() + dt.timedelta(days=40)
ics = ("BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nDTSTART:" + d0.strftime("%Y%m%dT%H%M%S") + "\r\nSUMMARY:Dentist\\, Dr. Rao\r\nEND:VEVENT\r\n"
       "BEGIN:VEVENT\r\nDTSTART;VALUE=DATE:" + (dt.date.today() + dt.timedelta(days=2)).strftime("%Y%m%d") + "\r\nSUMMARY:Holiday\r\nEND:VEVENT\r\n"
       "BEGIN:VEVENT\r\nDTSTART:" + d1.strftime("%Y%m%dT%H%M%S") + "\r\nSUMMARY:Far away\r\nEND:VEVENT\r\n"
       "BEGIN:VEVENT\r\nDTSTART:" + (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=3)).strftime("%Y%m%dT%H%M%SZ") + "\r\nSUMMARY:Past one\r\nRRULE:FREQ=WEEKLY\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")
(WORK / "cal.ics").write_text(ics)
rc, out = jeeg("calendar", "feed", "add", "work", str(WORK / "cal.ics")); ok(rc == 0, "calendar add a file")
rc, out = jeeg("calendar", "feed", "upcoming"); ok("Dentist, Dr. Rao" in out and "Holiday" in out and "all day" in out and "Far away" not in out and "Past one" not in out and "not expand" in out, "calendar upcoming 7 days: " + out)
rc, out = jeeg("calendar", "feed", "upcoming", "60"); ok("Far away" in out, "calendar upcoming 60 days")
class ICS(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        d = ics.encode(); self.send_response(200); self.send_header("Content-Length", str(len(d))); self.end_headers(); self.wfile.write(d)
ics_s, icsp = server(ICS)
rc, out = jeeg("calendar", "feed", "add", "net", f"http://127.0.0.1:{icsp}/secret/feed.ics"); ok(rc == 0, "calendar add from a link")
rc, out = jeeg("calendar", "feed", "list"); ok("net" in out and "secret/feed.ics" not in out, "calendar list hides the link path")
rc, out = jeeg("calendar", "feed", "add", "pub", "http://example.com/x.ics"); ok(rc == 1, "plain http to the internet refused")
rc, out = jeeg("calendar", "feed", "add", "big", "/etc/passwd"); ok(rc == 1, "a non-calendar file is not read as one") 
ics_s.shutdown()

# =========================================================== adb (fake)
fake_bin("adb", 'case "$1" in devices) echo "List of devices attached"; echo "ABC123 device model:Pixel";; shell) if [ "$2" = dumpsys ]; then printf "  status: 2\\n  level: 87\\n"; else echo "SHELL:$@" >> "$ADBLOG"; fi;; exec-out) printf "\\211PNG\\r\\n\\032\\nXXXX";; *) echo "bad $@" >&2; exit 1;; esac')
aenv = dict(ENV, ADBLOG=str(WORK / "adb.log"), HOME=str(WORK))
rc, out = jeeg("android", "devices", env=aenv); ok("ABC123" in out, "adb devices")
rc, out = jeeg("android", "battery", env=aenv); ok("87%" in out and "charging" in out, "adb battery: " + out)
rc, out = jeeg("android", "screenshot", env=aenv); ok(rc == 0 and list((WORK / "Pictures").glob("android_*.png")), "adb screenshot saved: " + out)
rc, out = jeeg("android", "open", "https://example.com/a?b=1", env=aenv); ok(rc == 0 and "android.intent.action.VIEW" in (WORK / "adb.log").read_text(), "adb open")
for bad in ("https://x.com; rm -rf /", "javascript:alert(1)", "https://x.com/$(id)", "https://x.com/`id`"):
    rc, out = jeeg("android", "open", bad, env=aenv); ok(rc == 1, "adb open refuses " + bad)
(BIN / "adb").unlink(); rc, out = jeeg("android", "devices"); ok(rc == 1 and "platform-tools" in out, "adb missing is explained")

# =========================================================== serial (pyserial is optional)
rc, out = jeeg("serial", "ports"); ok(("pyserial" in out) or rc == 0, "serial: works or explains pyserial: " + out[:80])
rc, out = jeeg("serial", "send", "not/a/port", "hi"); ok(rc == 1, "serial refuses a strange port name")

# =========================================================== peers: two JeeGs talking
HOME2 = tempfile.mkdtemp(prefix="jeeg-cn-2-")
srv = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "connect ai safe no tunnel"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=dict(ENV, JEEG_HOME=HOME2), cwd=WORK, stdin=subprocess.DEVNULL)
head = ""
for _ in range(40):
    ln = srv.stdout.readline(); head += ln
    if "Every call is printed" in ln or not ln: break
lm = re.search(r"Local link \(this computer only\): (http://127\.0\.0\.1:\d+/\S+?/)\s", head); ok(lm is not None, "second JeeG printed its link: " + head[:200])
if lm:
    link = lm.group(1)
    rc, out = jeeg("peer", "add", "office", link + "mcp"); ok(rc == 0, "peer add")
    rc, out = jeeg("peer", "list"); ok("office" in out and link.split("/")[-2] not in out, "peer list hides the secret")
    rc, out = jeeg("peer", "run", "office", "gst 100 18", yes=True); ok(rc == 0 and "118" in out, "peer run reaches the other JeeG: " + out)
    rc, out = jeeg("peer", "run", "office", "open youtube", yes=True); ok(rc == 1 and "not allowed" in out, "the other JeeG's mode still applies")
srv.terminate(); srv.wait(5)
rc, out = jeeg("peer", "run", "office", "gst 100 18", yes=True); ok(rc == 1 and "Could not reach" in out, "a closed peer is explained")
rc, out = jeeg("peer", "add", "pub", "http://example.com/abc/"); ok(rc == 1, "peer refuses plain http to the internet")

# =========================================================== MCP client (JeeG uses an MCP server: its own)
rc, out = jeeg("mcp", "add", "self", "=", f'"{sys.executable}" "{ROOT / "jeeg.py"}" --mcp'); ok(rc == 0, "mcp add")
rc, out = jeeg("mcp", "list"); ok("self" in out, "mcp list")
rc, out = jeeg("mcp", "tools", "self"); ok("jeeg_run" in out and "jeeg_find" in out, "mcp tools: " + out[:200])
rc, out = jeeg("mcp", "call", "self", "jeeg_run", '{"query": "gst 100 18"}', yes=True); ok(rc == 0 and "118" in out, "mcp call: " + out[:200])
rc, out = jeeg("mcp", "call", "self", "jeeg_run", "[1,2]", yes=True); ok(rc == 1, "mcp call needs a JSON object")
rc, out = jeeg("mcp", "call", "self", "nope_tool", "{}", yes=True); ok(rc == 1, "mcp unknown tool reported")
rc, out = jeeg("mcp", "add", "dead", "=", "/nonexistent/server"); rc, out = jeeg("mcp", "tools", "dead"); ok(rc == 1 and "Could not talk" in out, "a missing server is explained")
rc, out = jeeg("mcp", "call", "self", "jeeg_run", '{"query": "gst 100 18"}'); ok("118" not in out, "mcp call asks for confirmation without --yes")

# =========================================================== OpenAPI file and JavaScript client
oa = json.loads((ROOT / "integrations" / "openapi" / "jeeg-openapi.json").read_text())
ok(oa["openapi"].startswith("3.") and {"/v1/run", "/v1/find", "/v1/tasks", "/v1/health", "/v1/info", "/v1/categories", "/v1/task"} <= set(oa["paths"]), "openapi lists every route")
src = (ROOT / "jeeg_bridge.py").read_text()
ok(all(p in src for p in oa["paths"]), "every openapi route exists in the bridge")
def refs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "$ref": yield v
            else: yield from refs(v)
    elif isinstance(o, list):
        for v in o: yield from refs(v)
ok(all(r.split("/")[-1] in oa["components"]["schemas"] for r in refs(oa)), "every openapi $ref resolves")
import shutil
if shutil.which("node"):
    r = subprocess.run(["node", str(ROOT / "integrations" / "js" / "test.js")], capture_output=True, text=True, env=dict(os.environ, PYTHON=sys.executable), timeout=120)
    ok(r.returncode == 0 and "FAIL" not in r.stdout and "passed" in r.stdout, "javascript client: " + (r.stdout + r.stderr)[-300:])
else:
    print("note: node is not installed, JavaScript client test skipped")

print(f"connect: {P} passed, {F} failed")
sys.exit(1 if F else 0)
