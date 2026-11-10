"""Fuzz test: odd input must never crash the phrase router, the AI-mode argument parser, MCP handling or the AI-mode server.
Deterministic (fixed seed), a few seconds. Run with a different seed:  python tests/test_fuzz.py 123"""
import http.client, json, os, random, string, sys, tempfile, threading, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
HOME = tempfile.mkdtemp(prefix="jeeg-fz-"); os.environ["JEEG_HOME"] = HOME
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 20261110
rnd = random.Random(SEED)
P = F = 0
def ok(c, label):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", label)
import jeeg, jeeg_api, jeeg_remote as R, jeeg_bridge

WORDS = ["open", "gst", "100", "18", "then", "and", ";", "&", "convert", "km", "miles", "timer", "5", "minutes", "shutdown", "delete", "file", "../..", "~", "\\\\server\\share",
         "%s", "{0}", "$(id)", "`id`", "'", '"', "\x00", "‮", "नमस्ते", "₹", "💥", "-1", "1e999", "nan", "http://x", "*", "?", "(", ")", "[", "]", "--yes", "web", "update", "set", "search"]
def junk(n=None):
    n = n or rnd.randint(0, 12)
    parts = []
    for _ in range(n):
        r = rnd.random()
        if r < 0.55: parts.append(rnd.choice(WORDS))
        elif r < 0.8: parts.append("".join(rnd.choice(string.printable) for _ in range(rnd.randint(1, 12))))
        else: parts.append("".join(chr(rnd.randint(1, 0x2FFF)) for _ in range(rnd.randint(1, 6))))
    return " ".join(parts)

# 1. the router never raises
bad = []
for _ in range(1500):
    q = junk()
    try:
        jeeg_api.find(q, 3, home=HOME)
        jeeg_api.plan(q, home=HOME)
    except Exception as ex:
        bad.append((q, type(ex).__name__, str(ex)[:80]))
ok(not bad, f"router raised on {bad[:3]}")

# 2. the AI-mode option parser only ever raises ValueError
bad = []
for _ in range(1500):
    q = junk()
    try:
        R.parse_args(q)
    except ValueError:
        pass
    except Exception as ex:
        bad.append((q, type(ex).__name__))
ok(not bad, f"parse_args raised {bad[:3]}")

# 3. MCP handling of arbitrary JSON never raises and always answers sensibly
cfg = jeeg_bridge._cfg(home=HOME, policy=jeeg_bridge.Policy(only=R._safe_list()))
def rjson(d=0):
    r = rnd.random()
    if d > 3 or r < 0.3: return rnd.choice([None, True, False, 0, -1, 1.5, "", junk(2), "tools/call", "initialize"])
    if r < 0.6: return [rjson(d + 1) for _ in range(rnd.randint(0, 3))]
    return {rnd.choice(["jsonrpc", "id", "method", "params", "name", "arguments", "query", junk(1)]): rjson(d + 1) for _ in range(rnd.randint(0, 4))}
bad = []
for _ in range(1500):
    m = rjson()
    if isinstance(m, dict) and rnd.random() < 0.7:
        m.update({"jsonrpc": "2.0", "method": rnd.choice(["initialize", "ping", "tools/list", "tools/call", "nope", junk(1)])})
        if rnd.random() < 0.6: m["id"] = rnd.randint(1, 9)
    try:
        a = jeeg_bridge.mcp_handle(m, cfg)
        assert a is None or isinstance(a, dict)
    except Exception as ex:
        bad.append((str(m)[:80], type(ex).__name__))
ok(not bad, f"mcp_handle raised {bad[:3]}")

# 4. run_for_ai with random text under every mode: never raises, never runs a refused thing
bad = []
class No(R.Approver):
    def ask(self, text, key=""): return False
for mode in ("safe", "read", "ask", "god"):
    for _ in range(120):
        q = junk()
        if mode == "god" and any(w in q.lower() for w in ("shutdown", "delete", "restart", "sleep", "kill", "empty", "shred", "log out", "lock")):
            continue                                     # god mode would really run these; the point here is crashes, not actions
        if mode == "god": q = "gst " + "".join(c for c in q if c.isdigit() or c == " ")[:30]
        try:
            text, err = R.run_for_ai(q, mode, No(), HOME, log=lambda *_: None)
            assert isinstance(text, str) and isinstance(err, bool)
        except Exception as ex:
            bad.append((mode, q[:60], type(ex).__name__, str(ex)[:60]))
ok(not bad, f"run_for_ai raised {bad[:3]}")

# 5. the AI-mode server survives random HTTP
rs = R.RemoteState("ask", 5, HOME, No(), log=lambda *_: None, limit=100000)
rs.approver.phone = R.PhoneApprovals(); rs.approve_base = "/" + R.secrets.token_urlsafe(16) + "/"; rs.pin = "123456"
h = R.http.server.ThreadingHTTPServer(("127.0.0.1", 0), R.make_handler(rs)); rs.httpd = h
port = h.server_address[1]; rs.hosts = {f"127.0.0.1:{port}"}
threading.Thread(target=h.serve_forever, daemon=True).start()
paths = [rs.base_path, rs.base_path + "run", rs.base_path + "mcp", rs.base_path + "find", rs.base_path + "tasks", rs.approve_base, rs.approve_base + "pending",
         rs.approve_base + "answer", "/", "/x", rs.base_path[:-1], rs.base_path + "../", rs.base_path + "%00", "/" + "A" * 3000]
codes, errors = set(), []
for i in range(600):
    method = rnd.choice(["GET", "POST", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"])
    path = rnd.choice(paths) + rnd.choice(["", "", "?q=" + junk(3).replace(" ", "%20").replace("\x00", ""), "/" + junk(1).replace(" ", "")[:20].encode("ascii", "ignore").decode()])
    body = None
    hdr = {}
    if method in ("POST", "PUT", "PATCH"):
        body = rnd.choice([json.dumps(rjson()), json.dumps({"query": junk()}), json.dumps({"id": junk(1), "allow": rnd.choice([True, "x", 1, None]), "always": rnd.choice([True, 1])}),
                           junk(), "", "{", "\x00\x01\x02"]).encode("utf-8", "replace")
    if rnd.random() < 0.3: hdr["X-JeeG-Pin"] = rnd.choice(["123456", "000000", junk(1)[:10].encode("ascii", "ignore").decode()])
    if rnd.random() < 0.15: hdr["Origin"] = rnd.choice(["http://evil.example", f"http://127.0.0.1:{port}", "null"])
    if rnd.random() < 0.1: hdr["Host"] = "evil.example"
    try:
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=20)
        c.request(method, path.replace(" ", "%20"), body=body, headers=hdr)
        r = c.getresponse(); r.read(); codes.add(r.status); c.close()
    except (ConnectionError, http.client.HTTPException, OSError, ValueError, UnicodeError) as ex:
        if not isinstance(ex, (UnicodeError, ValueError, http.client.InvalidURL)): errors.append((method, path[:40], type(ex).__name__))
ok(not [c for c in codes if c >= 500], f"server answered with a 5xx: {sorted(codes)}")
ok(not errors, f"connection errors: {errors[:3]}")
c = http.client.HTTPConnection("127.0.0.1", port, timeout=20); c.request("GET", rs.base_path); r = c.getresponse()
ok(r.status in (200, 403, 429), f"the server is still alive after fuzzing ({r.status})")
h.shutdown()

print(f"fuzz (seed {SEED}): {P} passed, {F} failed")
sys.exit(1 if F else 0)
