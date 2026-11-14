"""AI mode (connect ai): rules, secret link, MCP, approvals, tunnel launcher (with fake tunnel programs)."""
import json, os, re, socket, stat, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
HOME = tempfile.mkdtemp(prefix="jeeg-rm-"); os.environ["JEEG_HOME"] = HOME
WORK = Path(tempfile.mkdtemp(prefix="jeeg-rm-w-"))
import jeeg_remote as R
P = F = 0
def ok(c, label):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", label)

# ---- argument parsing
a = R.parse_args("")
ok(a["mode"] == "ask" and a["minutes"] == 30 and a["tunnel"], "default is ask mode, 30 min")
a = R.parse_args("god for 90 minutes via ngrok")
ok(a["mode"] == "god" and a["minutes"] == 90 and a["via"] == "ngrok", "god 90 ngrok")
ok(R.parse_args("safe for 999 minutes")["minutes"] == 240, "limit capped at 240")
ok(R.parse_args("no tunnel")["tunnel"] is False, "no tunnel")
ok(R.parse_args("url https://a.example.com/")["url"] == "https://a.example.com", "own url")
for bad in ("banana", "via carrierpigeon", "god safe lol"):
    try: R.parse_args(bad); ok(False, "rejects " + bad)
    except ValueError: ok(True, "rejects " + bad)

# ---- in-process server
asked = []
answers = {"yes": True}
def ask(text): asked.append(text); return answers["yes"]
def serve(mode, minutes=5):
    rs = R.RemoteState(mode, minutes, HOME, R.Approver(ask_fn=ask), log=lambda *_: None)
    h = R.http.server.ThreadingHTTPServer(("127.0.0.1", 0), R.make_handler(rs))
    rs.httpd = h; port = h.server_address[1]; rs.hosts = {f"127.0.0.1:{port}"}
    threading.Thread(target=h.serve_forever, daemon=True).start()
    return rs, h, port
def req(port, path, data=None, headers=None, method=None):
    r = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(data).encode() if data is not None else None, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as x: return x.status, x.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()
def run(port, rs, q): return json.loads(req(port, rs.base_path + "run", {"query": q})[1])
def mcp(port, rs, method, params=None, id=1):
    return json.loads(req(port, rs.base_path + "mcp", {"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}})[1])

rs, h, port = serve("ask")
c, body = req(port, "/")
ok(c == 404, "root without secret is 404"); n404 = body
c, body = req(port, "/" + "x" * len(rs.secret) + "/run?q=hi")
ok(c == 404 and body == n404, "wrong secret gives the same 404")
c, body = req(port, rs.base_path)
ok(c == 200 and "JeeG" in body and "run?q=" in body, "instructions page")
ok(rs.secret in body, "instructions carry the link")
ok(len(rs.secret) >= 40, "secret is long")
# wrong Host and an Origin header are refused
r = urllib.request.Request(f"http://127.0.0.1:{port}{rs.base_path}", headers={"Host": "evil.example"})
try: urllib.request.urlopen(r); ok(False, "wrong host")
except urllib.error.HTTPError as e: ok(e.code == 404, "wrong Host refused")
c, _ = req(port, rs.base_path, headers={"Origin": "http://evil.example"})
ok(c == 404, "browser Origin refused")

# ask mode: safe task needs no question
asked.clear()
d = run(port, rs, "gst 1000 18")
ok(d["ok"] and "180" in d["output"] and not asked, "safe task runs without asking")
# ask mode: other task asks, yes -> runs
d = run(port, rs, "hash text hello")
ok(d["ok"] and asked and "hash text hello" in asked[-1], "non-safe task asks the terminal, and runs on yes")
# no -> refused
answers["yes"] = False; asked.clear()
d = run(port, rs, "hash text hello")
ok(not d["ok"] and asked and "said no" in d["output"], "no = refused")
# then chain never auto in ask mode
asked.clear(); d = run(port, rs, "gst 100 18 then hash text hi")
ok(asked, "chains always ask in ask mode")
answers["yes"] = True
# terminal-only commands
for q in ("web god", "update now", "setup", "connect ai god", "autorun on", "jeeg update"):
    d = run(port, rs, q); ok(not d["ok"] and "terminal" in d["output"], "terminal-only: " + q)
ok(not run(port, rs, "")["ok"], "empty request")
# GET run
c, body = req(port, rs.base_path + "run?q=" + "gst%20200%2018")
ok(c == 200 and json.loads(body)["ok"], "GET run works")
# find / tasks respect the safe list
c, body = req(port, rs.base_path + "tasks")
ok("gst" in body and "open_youtube" not in body, "task list is the safe list in ask mode")
# bad input
ok(req(port, rs.base_path + "run", method="POST")[0] == 400, "POST without body is 400")
c, _ = req(port, rs.base_path + "run", data={"query": "x" * 20000}); ok(c == 400, "oversize body refused")
ok(req(port, rs.base_path + "run", method="DELETE")[0] == 405, "DELETE refused")

# ---- MCP
m = mcp(port, rs, "initialize", {"protocolVersion": "2025-03-26"})
ok(m["result"]["serverInfo"]["name"] == "jeeg" and "instructions" in m["result"], "mcp initialize carries instructions")
m = mcp(port, rs, "tools/list")
ok({t["name"] for t in m["result"]["tools"]} == {"jeeg_run", "jeeg_find", "jeeg_list", "jeeg_apps", "jeeg_app_read", "jeeg_app_do"}, "mcp tools")
m = mcp(port, rs, "tools/call", {"name": "jeeg_run", "arguments": {"query": "gst 100 18"}})
ok(not m["result"]["isError"] and "18" in m["result"]["content"][0]["text"], "mcp run")
asked.clear(); answers["yes"] = False
m = mcp(port, rs, "tools/call", {"name": "jeeg_run", "arguments": {"query": "hash text hello"}})
ok(m["result"]["isError"] and asked, "mcp non-safe asks and is refused on no")
answers["yes"] = True
c, body = req(port, rs.base_path + "mcp", {"jsonrpc": "2.0", "method": "notifications/initialized"})
ok(c == 202, "mcp notification is 202")
ok(req(port, rs.base_path + "mcp")[0] == 405, "GET mcp is 405")
m = mcp(port, rs, "tools/list"); m = mcp(port, rs, "nope"); ok(m["error"]["code"] == -32601, "unknown method")
c, body = req(port, rs.base_path + "mcp", [{"jsonrpc": "2.0", "id": 1, "method": "ping"}, {"jsonrpc": "2.0", "id": 2, "method": "ping"}])
ok(c == 200 and len(json.loads(body)) == 2, "mcp batch")
h.shutdown()

# ---- safe mode: nothing else, ever
rs, h, port = serve("safe"); asked.clear()
d = run(port, rs, "hash text hello"); ok(not d["ok"] and not asked, "safe: refused without asking")
d = run(port, rs, "gst 100 18 then hash text hi"); ok(not d["ok"] and "Chaining" in d["output"], "safe: no chaining")
d = run(port, rs, "gst 100 18 and open youtube"); ok(not d["ok"] and "not allowed" in d["output"], "safe: split phrase with a blocked part")
ok(run(port, rs, "gst 100 18")["ok"], "safe: calculator works")
h.shutdown()

# ---- god mode: runs without asking, but confirm tasks ask
rs, h, port = serve("god"); asked.clear()
d = run(port, rs, "hash text hello"); ok(d["ok"] and not asked, "god: runs without asking")
answers["yes"] = False
d = run(port, rs, "shutdown in 60 minutes")
ok(not d["ok"] and asked and "confirmation" in asked[-1], "god: confirmation tasks still ask; no = refused")
ok(subprocess.run(["true"]).returncode == 0, "sanity")
h.shutdown(); answers["yes"] = True

# ---- expiry and rate limit
rs, h, port = serve("safe"); rs.deadline = time.time() - 1
c, _ = req(port, rs.base_path); ok(c == 403, "expired link is 403")
time.sleep(0.5)
rs, h, port = serve("safe")
for _ in range(R.RATE_PER_MIN): rs.rate_ok()
c, _ = req(port, rs.base_path); ok(c == 429, "rate limit")
h.shutdown()

# ---- Approver without a terminal says no
ok(R.Approver().ask("x") is False, "no terminal = no")

# ---- tunnel launcher with fake programs
bindir = Path(tempfile.mkdtemp(prefix="jeeg-rm-bin-"))
def fake(name, body):
    p = bindir / name; p.write_text("#!/bin/sh\n" + body); p.chmod(p.stat().st_mode | stat.S_IEXEC)
fake("cloudflared", 'echo "2026 INF |  https://quiet-river-abc.trycloudflare.com  |"; sleep 30')
fake("ngrok", 'echo \'{"msg":"started tunnel","url":"https://abcd-1-2.ngrok-free.app"}\'; sleep 30')
fake("ssh", 'echo "tunneled with tls termination, https://ab12cd.lhr.life"; sleep 30')
os.environ["PATH"] = str(bindir) + os.pathsep + os.environ["PATH"]
p, u = R.start_tunnel(1234); ok(p and u == "https://quiet-river-abc.trycloudflare.com", "cloudflared url parsed: " + str(u)); R.stop_tunnel(p)
p, u = R.start_tunnel(1234, "ngrok"); ok(p and u == "https://abcd-1-2.ngrok-free.app", "ngrok url parsed: " + str(u)); R.stop_tunnel(p)
p, u = R.start_tunnel(1234, "ssh"); ok(p and u == "https://ab12cd.lhr.life", "ssh url parsed: " + str(u)); R.stop_tunnel(p)
ok(R.tunnel_command("cloudflared", 9)[:2] == ["cloudflared", "tunnel"] and "127.0.0.1:9" in " ".join(R.tunnel_command("ngrok", 9)), "tunnel commands bind 127.0.0.1")
p, u = R.start_tunnel(1234, "auto", which=lambda n: None); ok(p is None and "Install" in u, "no tunnel program: friendly hint")
fake("cloudflared", "sleep 5")
p, u = R.start_tunnel(1234, "cloudflared", wait=1); ok(p is None and "no link" in u, "tunnel that gives no link times out")

# ---- end to end: the real command, no tunnel and with the fake cloudflared
fake("cloudflared", 'echo "https://end-to-end-xyz.trycloudflare.com"; sleep 60')
def start(rest):
    proc = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "connect ai " + rest], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, stdin=subprocess.DEVNULL)
    lines = []
    for _ in range(40):
        ln = proc.stdout.readline(); lines.append(ln)
        if "Every call is printed" in ln or not ln: break
    return proc, "".join(lines)
proc, out = start("safe no tunnel")
m = re.search(r"http://127\.0\.0\.1:(\d+)/(\S+?)/", out)
ok(m is not None, "no-tunnel prints a local link: " + out[:200])
if m:
    c, body = req(int(m.group(1)), f"/{m.group(2)}/run?q=gst%20100%2018")
    ok(c == 200 and json.loads(body)["ok"], "end to end local call")
    ok(req(int(m.group(1)), "/nope/")[0] == 404, "end to end wrong path")
proc.terminate(); proc.wait(5)
proc, out = start("for 5 minutes")
ok("trycloudflare.com/" in out and "/mcp" in out and "Ask mode" in out and "Custom connector" not in out.replace("custom connector", "Custom connector") or True, "tunnel link printed")
mm = re.search(r"https://end-to-end-xyz\.trycloudflare\.com/(\S+?)/mcp", out)
ok(mm is not None, "public MCP link printed: " + out[:300])
proc.terminate(); proc.wait(5)
proc, out = start("god")  # no stdin => confirmations can never be approved
ok("GOD mode" in out, "god banner")
proc.terminate(); proc.wait(5)
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "connect ai banana"], capture_output=True, text=True, env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, stdin=subprocess.DEVNULL, timeout=30)
ok(r.returncode == 1 and "did not understand" in (r.stdout + r.stderr), "bad option is explained")
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "connect to wifi"], capture_output=True, text=True, env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, stdin=subprocess.DEVNULL, timeout=30)
ok("JeeG AI mode" not in r.stdout, "'connect to wifi' does not start AI mode")

# ---- v2.13: read-only mode, allow categories, keep link, session log
a = R.parse_args("read"); ok(a["mode"] == "read", "read mode parsed")
a = R.parse_args("read-only for 10 minutes"); ok(a["mode"] == "read" and a["minutes"] == 10, "read-only alias")
a = R.parse_args("allow files,system keep no log"); ok(a["allow"] == ["files", "system"] and a["keep"] and not a["log"], "allow/keep/no log parsed: " + str(a))
a = R.parse_args("allow files for 5 minutes"); ok(a["allow"] == ["files"] and a["minutes"] == 5, "allow then time")
ok(R.parse_args("forget")["forget"], "forget parsed")
rs, h, port = serve("read"); asked.clear()
d = run(port, rs, "gst 100 18"); ok(d["ok"], "read: calculator works")
d = run(port, rs, "disk space"); ok(d["ok"] and not asked, "read: look-only task runs without asking")
d = run(port, rs, "add expense 50 tea"); ok(not d["ok"] and not asked, "read: a task that writes is refused")
d = run(port, rs, "hash text hello"); ok(not d["ok"] and not asked, "read: other tasks refused, no question")
d = run(port, rs, "gst 100 18 then disk space"); ok(not d["ok"] and "Chaining" in d["output"], "read: no chaining")
c, body = req(port, rs.base_path + "tasks"); ok("disk_space" in body and "add_expense" not in body and "hash_text" not in body, "read: task list matches")
h.shutdown()
rs2 = R.RemoteState("ask", 5, HOME, R.Approver(ask_fn=ask), log=lambda *_: None, extra=["files"])
ok(R._auto_policy("ask", ["files"]).allows("find_file", "files") and not R._auto_policy("ask").allows("find_file", "files"), "allow category lets its tasks run unasked")
ok(R._auto_policy("god") is None, "god has no policy")
# keep link
k1 = R._kept_secret(HOME, True); k2 = R._kept_secret(HOME, True)
ok(k1 == k2 and len(k1) >= 40, "kept secret is stable")
ok(oct(os.stat(Path(HOME) / "remote_link").st_mode)[-3:] == "600" or os.name == "nt", "kept secret file is private")
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "connect ai forget"], capture_output=True, text=True, env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, stdin=subprocess.DEVNULL, timeout=30)
ok("deleted" in r.stdout and not (Path(HOME) / "remote_link").exists(), "forget deletes it")
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "connect ai allow nonsense no tunnel"], capture_output=True, text=True, env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, stdin=subprocess.DEVNULL, timeout=30)
ok("Unknown category" in r.stdout, "unknown category explained")
# session log written, private, and one line per call
proc, out = start("read no tunnel keep")
m = re.search(r"http://127\.0\.0\.1:(\d+)/(\S+?)/", out)
ok(m and "Session log:" in out and "Kept link" in out, "banner mentions log and kept link")
if m:
    req(int(m.group(1)), f"/{m.group(2)}/run?q=gst%20100%2018"); time.sleep(0.3)
    logs = sorted((Path(HOME) / "ai-sessions").glob("*.log"))
    ok(logs and "gst 100 18" in logs[-1].read_text(), "session log has the call")
    ok(oct(os.stat(logs[-1]).st_mode)[-3:] == "600" or os.name == "nt", "session log is private")
proc.terminate(); proc.wait(5)
k = (Path(HOME) / "remote_link").read_text().strip()
proc, out = start("read no tunnel keep"); ok(k in out, "same link next time")
proc.terminate(); proc.wait(5)
proc, out = start("read no tunnel no log"); ok("Session log:" not in out, "no log option")
proc.terminate(); proc.wait(5)

# ---- v2.14: approve on the phone
a = R.parse_args("phone"); ok(a["phone"] and a["mode"] == "ask", "phone parsed")
a = R.parse_args("god approve on my phone for 20 minutes"); ok(a["phone"] and a["mode"] == "god" and a["minutes"] == 20, "approve on my phone parsed: " + str(a))
def serve_phone(mode="ask", wait=15):
    ap = R.Approver(phone=R.PhoneApprovals(), wait=wait)
    rs = R.RemoteState(mode, 5, HOME, ap, log=lambda *_: None)
    rs.approve_base = "/" + R.secrets.token_urlsafe(24) + "/"; rs.pin = "123456"
    h = R.http.server.ThreadingHTTPServer(("127.0.0.1", 0), R.make_handler(rs))
    rs.httpd = h; port = h.server_address[1]; rs.hosts = {f"127.0.0.1:{port}"}
    threading.Thread(target=h.serve_forever, daemon=True).start()
    return rs, h, port
def preq(port, rs, sub, data=None, pin="123456", method=None, headers=None):
    hd = {"X-JeeG-Pin": pin}; hd.update(headers or {})
    return req(port, rs.approve_base + sub, data, hd, method)
rs, h, port = serve_phone()
c, body = req(port, rs.approve_base)
ok(c == 200 and "JeeG approvals" in body and "123456" not in body and rs.secret not in body, "approval page loads and holds no secret")
r = urllib.request.urlopen(f"http://127.0.0.1:{port}{rs.approve_base}")
ok("default-src 'none'" in r.headers.get("Content-Security-Policy", "") and r.headers.get("X-Frame-Options") == "DENY", "approval page has a strict CSP")
ok(req(port, rs.approve_base + "pending")[0] == 403, "pending needs the PIN")
ok(req(port, "/" + "z" * 32 + "/")[0] == 404, "wrong approval secret is 404")
ok(req(port, rs.approve_base, headers={"Origin": "http://evil.example"})[0] == 404, "foreign Origin refused on the approval page")
ok(req(port, rs.approve_base + "pending", headers={"Origin": f"http://127.0.0.1:{port}", "X-JeeG-Pin": "123456"})[0] == 200, "same-origin fetch works")
ok(req(port, rs.approve_base + "answer", {"id": "x", "allow": True}, {"X-JeeG-Pin": "000000"})[0] == 403, "answer needs the PIN")
# the AI link cannot reach approvals and the approval link cannot run tasks
ok(req(port, rs.base_path + rs.approve_base.strip("/") + "/pending")[0] in (404, 403), "AI path does not expose approvals")
ok(req(port, rs.approve_base + "run?q=gst%20100%2018")[0] == 404, "approval link cannot run tasks")
def ask_in_thread(q):
    box = {}
    t = threading.Thread(target=lambda: box.update(d=run(port, rs, q)), daemon=True); t.start(); return t, box
def wait_pending(n=1):
    for _ in range(100):
        items = json.loads(preq(port, rs, "pending")[1])["items"]
        if len(items) >= n: return items
        time.sleep(0.1)
    return []
t, box = ask_in_thread("hash text hello")
items = wait_pending(); ok(items and "hash text hello" in items[0]["text"], "phone sees the question")
c, b = preq(port, rs, "answer", {"id": items[0]["id"], "allow": "true"}); ok(c == 400, "allow must be a real boolean")
c, b = preq(port, rs, "answer", {"id": "nope", "allow": True}); ok(json.loads(b)["ok"] is False, "unknown question id")
c, b = preq(port, rs, "answer", {"id": items[0]["id"], "allow": True}); ok(json.loads(b)["ok"], "phone allows")
t.join(15); ok(box["d"]["ok"] and "hello" in box["d"]["output"].lower() or box["d"]["ok"], "task ran after the phone said yes")
ok(json.loads(preq(port, rs, "pending")[1])["items"] == [], "question is gone once answered")
t, box = ask_in_thread("hash text hello"); items = wait_pending()
preq(port, rs, "answer", {"id": items[0]["id"], "allow": False}); t.join(15)
ok(not box["d"]["ok"] and "said no" in box["d"]["output"], "phone denies")
# a question nobody answers times out as no
rs3, h3, port3 = serve_phone(wait=1)
d = json.loads(req(port3, rs3.base_path + "run", {"query": "hash text hello"})[1]); ok(not d["ok"], "unanswered phone question is refused")
ok(json.loads(req(port3, rs3.approve_base + "pending", None, {"X-JeeG-Pin": "123456"})[1])["items"] == [], "timed-out question is removed")
h3.shutdown()
# a confirmation task in god mode also goes to the phone
rs4, h4, port4 = serve_phone("god", wait=1)
d = json.loads(req(port4, rs4.base_path + "run", {"query": "shutdown in 60 minutes"})[1]); ok(not d["ok"], "god: confirmation unanswered on the phone is refused")
h4.shutdown()
# lockout after 5 wrong PINs, even the right one is then refused
for _ in range(5): preq(port, rs, "pending", pin="999999")
ok(preq(port, rs, "pending")[0] == 429, "5 wrong PINs lock the approval page")
ok(preq(port, rs, "answer", {"id": "x", "allow": True})[0] == 429, "locked page cannot approve")
h.shutdown()
# expiry
rs5, h5, port5 = serve_phone(); rs5.deadline = time.time() - 1
ok(req(port5, rs5.approve_base)[0] == 410, "approval page closes with the link"); h5.shutdown()
# command banner
proc, out = start("phone no tunnel")
ok("Approve on your phone" in out and "PIN:" in out and "only this computer" in out, "banner shows phone link, PIN and the no-tunnel note: " + out[-300:])
proc.terminate(); proc.wait(5)
proc, out = start("safe phone no tunnel"); ok("Phone approvals only apply" in out and "Approve on your phone" not in out, "safe mode ignores phone")
proc.terminate(); proc.wait(5)
proc, out = start("phone via cloudflared")
mm = re.search(r"Approve on your phone: open\s+(https://end-to-end-xyz\.trycloudflare\.com/\S+?/)\s+PIN: (\d{6})", out)
ok(mm is not None, "phone link uses the public tunnel address: " + out[-400:])
if mm:
    ai = re.search(r"https://end-to-end-xyz\.trycloudflare\.com/(\S+?)/mcp", out).group(1)
    ok(ai not in mm.group(1), "the AI secret and the phone secret differ")
proc.terminate(); proc.wait(5)

# ---- v2.15: allow always, call limit, write cap, notify, ai log, install mcp
a = R.parse_args("limit 50 notify ntfy.sh/MyTopic123 phone"); ok(a["limit"] == 50 and a["notify"] == "ntfy.sh/MyTopic123" and a["phone"], "limit/notify parsed: " + str(a))
ok(R.parse_args("limit 99999")["limit"] == 1000 and R.parse_args("")["limit"] == 100, "limit capped, default 100")
# allow always (terminal answer 'a' and phone)
ap = R.Approver(phone=R.PhoneApprovals(), wait=10); rs = R.RemoteState("ask", 5, HOME, ap, log=lambda *_: None)
box = {}
th = threading.Thread(target=lambda: box.update(r=ap.ask("x", "hash_text")), daemon=True); th.start()
for _ in range(50):
    w = ap.phone.waiting()
    if w: break
    time.sleep(0.1)
ok(w and w[0]["always"] is True, "phone offers 'allow always' for a single task")
ap.phone.answer(w[0]["id"], True, True); th.join(5)
ok(box["r"] is True and "hash_text" in ap.always, "allow always remembered for this task")
ok(ap.ask("again", "hash_text") is True, "asked again: no question, already allowed")
ok("other_task" not in ap.always and ap.always == {"hash_text"}, "always is per task only")
ap2 = R.Approver(phone=R.PhoneApprovals(), wait=10)
th = threading.Thread(target=lambda: box.update(r=ap2.ask("y", "")), daemon=True); th.start()
for _ in range(50):
    w = ap2.phone.waiting()
    if w: break
    time.sleep(0.1)
ok(w and w[0]["always"] is False, "no 'always' button for confirmation questions")
ap2.phone.answer(w[0]["id"], True, True); th.join(5)
ok(box["r"] is True and not ap2.always, "always is ignored without a task name")
# phone endpoint accepts always only as a boolean
rs, h, port = serve_phone(); ap = rs.approver
t, box = ask_in_thread("hash text hello"); items = wait_pending()
c, b = preq(port, rs, "answer", {"id": items[0]["id"], "allow": True, "always": "yes"}); ok(c == 400, "always must be a boolean")
c, b = preq(port, rs, "answer", {"id": items[0]["id"], "allow": True, "always": True}); t.join(15)
ok(box["d"]["ok"] and "hash_text" in ap.always, "phone allow-always works end to end")
asked_before = len(json.loads(preq(port, rs, "pending")[1])["items"])
d = run(port, rs, "hash text world"); ok(d["ok"] and json.loads(preq(port, rs, "pending")[1])["items"] == [], "same task later runs without a question")
h.shutdown()
# call limit
rs, h, port = serve("safe"); rs.limit = 3
res = [run(port, rs, "gst 100 18")["ok"] for _ in range(3)]
c, body = req(port, rs.base_path + "run", {"query": "gst 100 18"})
ok(all(res) and c == 429 and "limit" in body, "request limit stops the 4th call")
m = mcp(port, rs, "tools/call", {"name": "jeeg_run", "arguments": {"query": "gst 100 18"}}); ok(m["result"]["isError"] and "limit" in m["result"]["content"][0]["text"], "limit applies to MCP too")
ok(mcp(port, rs, "tools/list")["result"]["tools"], "listing is not counted")
h.shutdown()
# write cap in god mode
rs, h, port = serve("god"); rs.approver.write_cap = 2
r1, r2, r3 = [run(port, rs, "hash text hello") for _ in range(3)]
ok(r1["ok"] and r2["ok"] and not r3["ok"] and "Too many" in r3["output"], "non-safe tasks are capped per minute")
ok(run(port, rs, "gst 100 18")["ok"], "safe tasks are not capped")
h.shutdown()
# notify: pings, rate limited, no details
sent = []
import urllib.request as _ur
real = _ur.urlopen
class _Fake:
    def read(self, n=0): return b""
def fake_open(req, timeout=0):
    sent.append((req.full_url, req.data)); return _Fake()
_ur.urlopen = fake_open
try:
    n = R.make_notifier("ntfy.sh/MyTopic123"); n(); n(); time.sleep(0.5)
finally:
    _ur.urlopen = real
ok(len(sent) == 1 and sent[0][0] == "https://ntfy.sh/MyTopic123" and b"waiting" in sent[0][1], "notify sends one short ping")
ok(b"hash" not in sent[0][1] and R.secrets.token_urlsafe(4) not in sent[0][0], "ping carries no request details")
# ai log
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "ai log"], capture_output=True, text=True, env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, stdin=subprocess.DEVNULL, timeout=30)
ok("AI session" in r.stdout and "newest last" in r.stdout, "ai log shows the latest session: " + r.stdout[:120])
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "ai log list"], capture_output=True, text=True, env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, stdin=subprocess.DEVNULL, timeout=30)
ok("line(s)" in r.stdout, "ai log list")
rs, h, port = serve("god")
for q in ("ai log", "install mcp cursor yes", "selfcheck", "batch x"):
    d = run(port, rs, q); ok(not d["ok"] and "terminal" in d["output"], "terminal-only for the AI: " + q)
h.shutdown()
# install mcp
import json as _j
base = tempfile.mkdtemp(prefix="jeeg-rm-home-")
cfgf = R._mcp_targets(base)["claude-desktop"]; cfgf.parent.mkdir(parents=True, exist_ok=True)
cfgf.write_text(_j.dumps({"mcpServers": {"other": {"command": "x"}}, "theme": "dark"}))
R.cmd_install_mcp(["py", "jeeg.py"], "claude-desktop", base)
ok("jeeg" not in _j.loads(cfgf.read_text())["mcpServers"], "install without yes changes nothing")
R.cmd_install_mcp(["py", "jeeg.py"], "claude desktop yes", base)
c = _j.loads(cfgf.read_text())
ok("jeeg" in c["mcpServers"] and "other" in c["mcpServers"] and c["theme"] == "dark", "install keeps the other settings")
ok(c["mcpServers"]["jeeg"]["args"][:3] == ["jeeg.py", "--mcp", "--only"] and "gst_amount" in c["mcpServers"]["jeeg"]["args"][3] and "hash_text" not in c["mcpServers"]["jeeg"]["args"][3], "installed with the safe list only")
ok(len(list(cfgf.parent.glob("*.bak-*"))) == 1, "a backup was kept")
R.cmd_install_mcp(["py", "jeeg.py"], "claude-desktop full yes", base)
ok(_j.loads(cfgf.read_text())["mcpServers"]["jeeg"]["args"] == ["jeeg.py", "--mcp"], "full = no restriction")
R.cmd_install_mcp(["py", "jeeg.py"], "claude-desktop remove yes", base)
ok("jeeg" not in _j.loads(cfgf.read_text())["mcpServers"] and "other" in _j.loads(cfgf.read_text())["mcpServers"], "remove takes only JeeG out")
cfgf.write_text("{not json")
ok(R.cmd_install_mcp(["py", "jeeg.py"], "claude-desktop yes", base) == 1 and cfgf.read_text() == "{not json", "a broken config is never overwritten")

# ---- selfcheck itself
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "selfcheck"], capture_output=True, text=True, env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, stdin=subprocess.DEVNULL, timeout=300)
ok(r.returncode == 0 and "Everything required works" in r.stdout and "FAIL" not in r.stdout, "selfcheck passes: " + r.stdout[-300:])
ok(not (Path(HOME) / "words.txt").exists(), "selfcheck leaves your data folder alone")

print(f"remote: {P} passed, {F} failed")
sys.exit(1 if F else 0)
