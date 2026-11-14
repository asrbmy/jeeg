"""Tests for the outside-program bridges: HTTP API, JSON lines, MCP."""
import io, json, os, socket, stat, sys, tempfile, threading, urllib.request, urllib.error
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["JEEG_HOME"] = tempfile.mkdtemp(prefix="jeeg-bridge-test-")
os.environ.pop("JEEG_API_TOKEN", None)
import jeeg, jeeg_bridge as B

P = F = 0
def ok(c, label):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", label)

# dispatch
d = B.dispatch({"query": "gst 2500 18"})
ok(d["ok"] and d["result"]["ok"] and d["result"]["task"] == "gst_amount", "run")
ok(B.dispatch({"op": "task", "name": "gst_amount", "args": [1000, 18]})["result"]["ok"], "task")
ok(B.dispatch({"name": "gst_amount", "args": [1000, 18]})["ok"], "task inferred")
ok(B.dispatch({"op": "find", "query": "open youtube", "limit": 2})["result"][0]["name"] == "open_youtube", "find")
ok(len(B.dispatch({"op": "tasks"})["result"]) >= 455 and B.dispatch({"op": "categories"})["ok"], "tasks/categories")
ok(B.dispatch({"op": "info", "name": "gst_amount"})["result"]["usage"], "info")
ok(B.dispatch({"op": "ping"})["result"]["jeeg"] == jeeg.__version__, "ping")
for bad in (5, [], {"op": "zzz"}, {"op": "run"}, {"op": "run", "query": 5}, {"op": "task", "name": "nope_zz"},
            {"op": "task", "name": "gst_amount", "args": "x"}, {"op": "info", "name": "nope_zz"}):
    r = B.dispatch(bad)
    ok(r["ok"] is False and r["error"], f"error handled {bad!r}")
c = B.dispatch({"query": "shutdown pc", "yes": True})
ok(c["result"]["needs_confirmation"], "yes ignored unless allowed")
ok(B.dispatch({"query": "web"})["result"]["exit"] == 1, "terminal-only")
ok(B.dispatch({"query": "gst 1 1", "timeout": "x"})["ok"], "bad timeout falls back")

# json lines
out = io.StringIO()
B.stdio_loop(stdin=io.StringIO('{"id":"a","query":"gst 100 5"}\n\nnot json\n[1]\n{"id":7,"op":"ping"}\n'), stdout=out)
rows = [json.loads(l) for l in out.getvalue().splitlines()]
ok(len(rows) == 4 and rows[0]["id"] == "a" and rows[0]["ok"] and not rows[1]["ok"] and not rows[2]["ok"] and rows[3]["id"] == 7, "stdio lines")

# MCP
def rpc(method, params=None, id=1):
    return B.mcp_handle({"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}})
ok(rpc("initialize", {"protocolVersion": "2025-03-26"})["result"]["serverInfo"]["name"] == "jeeg", "mcp initialize")
ok(B.mcp_handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None, "mcp notification")
ok([t["name"] for t in rpc("tools/list")["result"]["tools"]] == ["jeeg_run", "jeeg_find", "jeeg_list", "jeeg_apps", "jeeg_app_read", "jeeg_app_do"], "mcp tools")
r = rpc("tools/call", {"name": "jeeg_run", "arguments": {"query": "gst 2500 18"}})["result"]
ok(not r["isError"] and "2,950.00" in r["content"][0]["text"], "mcp run")
r = rpc("tools/call", {"name": "jeeg_run", "arguments": {"query": "shutdown pc"}})["result"]
ok(r["isError"] and "not run" in r["content"][0]["text"], "mcp refuses confirm tasks")
ok("open_youtube" in rpc("tools/call", {"name": "jeeg_find", "arguments": {"query": "open youtube"}})["result"]["content"][0]["text"], "mcp find")
ok("gst_amount" in rpc("tools/call", {"name": "jeeg_list", "arguments": {"category": "money"}})["result"]["content"][0]["text"], "mcp list")
ok(rpc("tools/call", {"name": "zzz"})["error"]["code"] == -32602, "mcp unknown tool")
ok(rpc("nope")["error"]["code"] == -32601, "mcp unknown method")
ok(B.mcp_handle("x")["error"]["code"] == -32600, "mcp invalid")
out = io.StringIO(); B.mcp_loop(stdin=io.StringIO("garbage\n"), stdout=out)
ok(json.loads(out.getvalue())["error"]["code"] == -32700, "mcp parse error")

# token
t = B.get_token()
ok(len(t) >= 30 and t == B.get_token(), "token stable")
tf = Path(os.environ["JEEG_HOME"]) / "api_token"
ok(tf.exists() and (os.name == "nt" or stat.S_IMODE(tf.stat().st_mode) == 0o600), "token file private")
os.environ["JEEG_API_TOKEN"] = "x" * 24
ok(B.get_token() == "x" * 24, "token env"); os.environ.pop("JEEG_API_TOKEN")

# HTTP
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
import http.server
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), B.make_handler(t, port, B._cfg()))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}"
def call(path, data=None, headers=None, token=t):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    h.update(headers or {})
    req = urllib.request.Request(base + path, data=data, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=20) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")
st, j = call("/v1/health"); ok(st == 200 and j["ok"], "http health")
st, j = call("/v1/find?q=open%20youtube&limit=1"); ok(st == 200 and j["result"][0]["name"] == "open_youtube", "http find")
st, j = call("/v1/tasks?category=money"); ok(st == 200 and all(x["category"] == "money" for x in j["result"]), "http tasks")
st, j = call("/v1/run", b'{"query":"gst 2500 18"}'); ok(st == 200 and j["result"]["ok"], "http run")
st, j = call("/v1/task", b'{"name":"gst_amount","args":[1000,18]}'); ok(st == 200 and j["result"]["ok"], "http task")
st, j = call("/v1/run", b'{"query":"shutdown pc","yes":true}'); ok(j["result"]["needs_confirmation"], "http cannot force confirm")
ok(call("/v1/tasks", token=None)[0] == 401, "http needs token")
ok(call("/v1/tasks", token="wrong")[0] == 401, "http wrong token")
ok(call("/v1/tasks", headers={"Origin": "http://evil.example"})[0] == 403, "http refuses browsers")
ok(call("/v1/tasks", headers={"Host": "evil.example"})[0] == 403, "http host check")
ok(call("/v1/zzz")[0] == 404, "http 404")
ok(call("/v1/run", b"not json")[0] == 400, "http bad json")
ok(call("/v1/run", b"[1]")[0] == 400, "http json not object")
st, _ = call("/v1/run", json.dumps({"query": "q" * 80000}).encode()); ok(st == 400, "http body limit")
st, j = call("/v1/run", json.dumps({"query": "q" * 3000}).encode()); ok(st == 200 and not j["ok"], "http long query refused")
httpd.shutdown(); httpd.server_close()

# the CLI flags
import subprocess
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "--stdio"], input='{"query":"gst 100 5"}\n', capture_output=True, text=True, timeout=60)
ok(json.loads(r.stdout)["ok"], "cli --stdio")
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "--api-token"], capture_output=True, text=True, timeout=60)
ok(r.stdout.strip() == t, "cli --api-token")
r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "--serve-api", "80"], capture_output=True, text=True, timeout=60)
ok("1024" in r.stdout, "cli port range")

# restricted callers (--only / --except)
pol = B.Policy(only=["money", "show_time"])
cfgp = B._cfg(policy=pol)
ok(B.dispatch({"query": "gst 2500 18"}, **cfgp)["result"]["ok"], "policy allows money")
r = B.dispatch({"query": "open youtube"}, **cfgp); ok(not r["ok"] and "not allowed" in r["error"], "policy blocks apps")
r = B.dispatch({"op": "task", "name": "open_youtube"}, **cfgp); ok(not r["ok"] and "not allowed" in r["error"], "policy blocks by name")
ok(B.dispatch({"op": "task", "name": "show_time"}, **cfgp)["result"]["ok"], "policy allows by task name")
ok(set(B.dispatch({"op": "categories"}, **cfgp)["result"]) == {"money", "time"}, "policy filters categories")
ok(all(x["category"] in ("money", "time") for x in B.dispatch({"op": "tasks"}, **cfgp)["result"]), "policy filters tasks")
ok(all(m["name"] != "open_youtube" for m in B.dispatch({"op": "find", "query": "open youtube"}, **cfgp)["result"]), "policy filters find")
ok(not B.dispatch({"op": "info", "name": "open_youtube"}, **cfgp)["ok"], "policy hides info")
r = B.dispatch({"query": "gst 100 5 and open youtube"}, **cfgp)
ok(not r["ok"] or r["result"]["task"] == "gst_amount" and len(r["result"]["output"]) < 400 and "youtube" not in r["result"]["output"].lower(), "policy: no multi-task bypass")
r = B.dispatch({"query": "history"}, **cfgp); ok(not r["ok"] or not r["result"]["ok"] or "gst" not in r["result"]["output"], "policy: no built-in commands")
pol2 = B.Policy(deny=["money"]); ok(not B.dispatch({"query": "gst 2500 18"}, **B._cfg(policy=pol2))["ok"], "deny list")
ok(B.Policy().active is False and B.Policy(only=[" "]).active is False, "empty policy inactive")

# audit log
lg = Path(tempfile.mkdtemp()) / "api.log"
B.dispatch({"query": "gst 777 5 secretword"}, **B._cfg(audit_path=lg)); B.dispatch({"op": "ping"}, **B._cfg(audit_path=lg))
txt = lg.read_text(); row = json.loads(txt.splitlines()[0])
ok(len(txt.splitlines()) == 1 and row["task"] == "gst_amount" and row["exit"] == 0 and "777" not in txt and "secretword" not in txt, "audit log has no content")
ok(os.name == "nt" or stat.S_IMODE(lg.stat().st_mode) == 0o600, "audit log private")

# robustness
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), B.make_handler(t, port, B._cfg()))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
ok(call("/v1/find?q=x&limit=%C2%B2")[0] == 200, "http non-ascii digit limit")
ok(call("/v1/find?q=x&limit=" + "9" * 50)[0] == 200, "http huge limit")
out = io.StringIO()
class Raw(io.TextIOWrapper): pass
raw = Raw(io.BytesIO(b'{"query":"gst 100 5"}\n\xff\xfe broken\n{"op":"ping"}\n'), encoding="utf-8", errors="strict")
B.stdio_loop(stdin=raw, stdout=out)
ok(len(out.getvalue().splitlines()) == 3, "invalid utf-8 on stdin does not crash")
os.environ["JEEG_API_TOKEN"] = "short"; ok(B.get_token() == t, "short env token ignored"); os.environ.pop("JEEG_API_TOKEN")
os.chmod(tf, 0o644); B.get_token(); ok(os.name == "nt" or stat.S_IMODE(tf.stat().st_mode) == 0o600, "token file re-tightened")
ok(jeeg.run("gst 100 5").to_dict()["ok"], "Result.to_dict")
ok(B.mcp_handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": []})["error"]["code"] == -32602, "mcp bad params")
ok(B.mcp_handle({"jsonrpc": "2.0", "id": 2, "method": ["x"]}) is None, "mcp bad method type")
cp = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "--stdio", "--only", "time"], input='{"query":"gst 100 5"}\n{"query":"show time"}\n', capture_output=True, text=True, timeout=60)
a, b = [json.loads(x) for x in cp.stdout.splitlines()]
ok(not a["ok"] and b["ok"], "cli --only")

httpd.shutdown(); httpd.server_close()
print(f"bridge tests: {P} passed, {F} failed")
sys.exit(1 if F else 0)
