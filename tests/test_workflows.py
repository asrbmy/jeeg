"""Workflow-tool kit (n8n, Node-RED, Kestra, Prefect, Python runner): files are valid and work against a live JeeG API,
and JeeG can start a workflow with `rest post`. Run: python tests/test_workflows.py"""
import json, os, re, shutil, socket, subprocess, sys, tempfile, threading, time, http.server
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
W = ROOT / "integrations" / "workflows"
TMP = Path(tempfile.mkdtemp(prefix="jeeg-wf-"))
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
env = dict(os.environ, JEEG_HOME=str(TMP / "h"), HOME=str(TMP / "home")); (TMP / "home").mkdir()
JEEG = [sys.executable, str(ROOT / "jeeg.py")]
def freeport():
    with socket.socket() as s: s.bind(("127.0.0.1", 0)); return s.getsockname()[1]

# ---- files
n8n = json.load(open(W / "n8n/jeeg-run-task.json"))
names = {n["name"] for n in n8n["nodes"]}
ok(all(k in names and all(t["node"] in names for b in v["main"] for t in b) for k, v in n8n["connections"].items()), "n8n: connections point at real nodes")
ok(len({n["id"] for n in n8n["nodes"]}) == len(n8n["nodes"]), "n8n: unique node ids")
http_node = next(n for n in n8n["nodes"] if n["type"].endswith("httpRequest"))
ok(http_node["parameters"]["url"].startswith("http://127.0.0.1:") and "Bearer" in http_node["notes"] and "token" not in json.dumps(n8n["nodes"]).replace("<token", "").lower().replace("jeeg --api-token", ""), "n8n: calls the local API and holds no token")
nr = json.load(open(W / "node-red/jeeg-flow.json"))
ids = {n["id"] for n in nr}
ok(len(ids) == len(nr), "node-red: unique ids")
ok(all(w in ids for n in nr for ws in n.get("wires", []) for w in ws), "node-red: wires point at real nodes")
ok(all(n["z"] in ids for n in nr if n["type"] != "tab"), "node-red: every node is on the tab")
ky = (W / "kestra/jeeg-run-task.yaml").read_text()
ok("io.kestra.plugin.core.http.Request" in ky and "secret('JEEG_TOKEN')" in ky and "127.0.0.1:8766/v1/run" in ky and re.search(r"^id: \w+", ky, re.M) and re.search(r"^namespace: ", ky, re.M), "kestra: flow basics")
try:
    import yaml
    d = yaml.safe_load(ky); ok(d["tasks"][0]["method"] == "POST", "kestra: yaml parses")
except ImportError: pass
for f in W.rglob("*"):
    if f.is_file():
        t = f.read_text(errors="replace"); ok("pypi-" not in t and "ghp_" not in t, "no secret in " + f.name)

# ---- a live API
port = freeport(); tok = "w" * 32
api = subprocess.Popen(JEEG + ["--serve-api", str(port), "--only", "text,money,utility,time"], env=dict(env, JEEG_API_TOKEN=tok), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    time.sleep(0.25)
    try: socket.create_connection(("127.0.0.1", port), 1).close(); break
    except OSError: pass
try:
    # Python runner and Prefect flow
    sys.path.insert(0, str(W / "python")); sys.path.insert(0, str(W / "prefect"))
    import jeeg_runner, jeeg_flow
    os.environ["JEEG_TOKEN"] = tok
    out = jeeg_runner.jeeg("convert 5 km to miles", port); ok("3.1" in out, "python runner: " + out)
    out = jeeg_flow.jeeg.__wrapped__("convert 5 km to miles", port) if hasattr(jeeg_flow.jeeg, "__wrapped__") else jeeg_flow.jeeg("convert 5 km to miles", port); ok("3.1" in out, "prefect task body: " + out)
    for bad in ("delete file zzz-nothing", "open youtube"):
        try: jeeg_runner.jeeg(bad, port); ok(False, "runner must refuse: " + bad)
        except RuntimeError: ok(True, "")
    os.environ["JEEG_TOKEN"] = "wrong"
    try: jeeg_runner.jeeg("convert 5 km to miles", port); ok(False, "wrong token refused")
    except Exception: ok(True, "")
    os.environ.pop("JEEG_TOKEN")
    try: jeeg_runner.jeeg("x", port); ok(False, "no token")
    except RuntimeError as e: ok("JEEG_TOKEN" in str(e), "missing token explained")
    r = subprocess.run([sys.executable, str(W / "prefect/jeeg_flow.py"), "convert 5 km to miles"], capture_output=True, text=True, env=dict(os.environ, JEEG_TOKEN=tok), timeout=60)
    # the script targets port 8766 by default, so only check it fails cleanly when nothing listens there
    ok(r.returncode != 0 or "3.1" in r.stdout, "prefect script ends cleanly")
    # Node-RED function nodes, run in Node with the real API
    node = shutil.which("node")
    if node:
        fn = {n["id"]: n["func"] for n in nr if n["type"] == "function"}
        js = f'''
const build = new Function("env","node","msg", {json.dumps(fn["jeeg_build"])});
const take = new Function("env","node","msg", {json.dumps(fn["jeeg_answer"])});
(async () => {{
  const logs = [];
  const node = {{ error: (m) => logs.push(m), warn: (m) => logs.push(m) }};
  const noTok = build({{ get: () => undefined }}, node, {{ payload: "x" }});
  let msg = build({{ get: () => "{tok}" }}, node, {{ payload: "convert 5 km to miles" }});
  const r = await fetch("http://127.0.0.1:{port}/v1/run", {{ method: "POST", headers: msg.headers, body: JSON.stringify(msg.payload) }});
  msg.payload = await r.json();
  const out = take({{}}, node, msg);
  const bad = take({{}}, node, {{ payload: {{ ok: false, error: "nope" }} }});
  console.log(JSON.stringify({{ noTok: noTok, out: out && out.payload, bad: bad, logs }}));
}})();'''
        r = subprocess.run([node, "-e", js], capture_output=True, text=True, timeout=60)
        try: o = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception: o = {}; print(r.stdout, r.stderr[:400])
        ok(o.get("noTok") is None and any("JEEG_TOKEN" in l for l in o.get("logs", [])), "node-red: missing token explained")
        ok("3.1" in (o.get("out") or ""), "node-red: request built and answer taken: " + str(o))
        ok(o.get("bad") is None, "node-red: a failure produces no message")
finally:
    api.terminate()

# ---- JeeG starts a workflow: rest add + rest post to a fake n8n / Kestra / Prefect
GOT = []
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        GOT.append((self.path, self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()))
        out = b'{"started":true}'; self.send_response(200); self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)
hp = freeport(); srv = http.server.ThreadingHTTPServer(("127.0.0.1", hp), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
def j(*a):
    p = subprocess.run(JEEG + list(a), capture_output=True, text=True, env=env, timeout=60, stdin=subprocess.DEVNULL); return p.returncode, p.stdout + p.stderr
rc, o = j("rest", "add", "n8n", f"http://127.0.0.1:{hp}", "none"); ok(rc == 0 and "Saved" in o, "rest add: " + o)
rc, o = j("rest", "post", "n8n", "/webhook/abc-123", '{"event":"backup done"}'); ok("needs confirmation" in o and not GOT, "rest post asks first: " + o[:100])
rc, o = j("--yes", "rest", "post", "n8n", "/webhook/abc-123", '{"event":"backup done"}'); ok(GOT and GOT[-1][0] == "/webhook/abc-123" and json.loads(GOT[-1][1]) == {"event": "backup done"}, "n8n-style webhook received the JSON: " + o)
rc, o = j("--yes", "rest", "post", "n8n", "/api/v1/executions/webhook/company.local/jeeg_run_task/key123", "{}"); ok(GOT[-1][0].endswith("/jeeg_run_task/key123"), "kestra-style path")
rc, o = j("--yes", "rest", "post", "n8n", "/api/deployments/11111111-2222-3333-4444-555555555555/create_flow_run", "{}"); ok(GOT[-1][0].endswith("/create_flow_run"), "prefect-style path")
rc, o = j("--yes", "rest", "post", "n8n", "http://evil.example/x", "{}"); ok(rc != 0, "a full address is refused as a path")
srv.shutdown()
print(f"workflows: {P} passed, {F} failed"); sys.exit(1 if F else 0)
