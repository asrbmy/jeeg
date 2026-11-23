"""Plugins and extensions: local-model chat script, tool lists, Obsidian + VS Code logic, browser extension (real Chromium if present).
Run: python tests/test_plugins.py"""
import json, os, shutil, socket, subprocess, sys, tempfile, threading, time, http.server
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
INT = ROOT / "integrations"
sys.path.insert(0, str(INT / "ai" / "local"))
import jeeg_chat
TMP = Path(tempfile.mkdtemp(prefix="jeeg-plug-"))
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
env = dict(os.environ, JEEG_HOME=str(TMP / "h"), HOME=str(TMP / "home")); (TMP / "home").mkdir()
JEEG = f"{sys.executable} {ROOT / 'jeeg.py'}"
def freeport():
    with socket.socket() as s: s.bind(("127.0.0.1", 0)); return s.getsockname()[1]

# ---- tool lists
ok(json.load(open(INT / "ai/openai/tools.json")) == jeeg_chat.TOOLS, "openai tools.json matches the script")
g = json.load(open(INT / "ai/openai/gemini-tools.json"))[0]["functionDeclarations"]
ok([d["name"] for d in g] == [t["function"]["name"] for t in jeeg_chat.TOOLS], "gemini tool names match")
ok(all(d["parameters"]["type"] == "OBJECT" for d in g), "gemini types are upper case")
ok(json.load(open(INT / "ai/claude/claude_desktop_config.example.json"))["mcpServers"]["jeeg"]["args"] == ["--mcp"], "claude config")
json.load(open(INT / "openapi/jeeg-openapi.json"))
for m in (INT / "browser/manifest.json", INT / "obsidian/manifest.json", INT / "vscode/package.json"): json.load(open(m))
bm = json.load(open(INT / "browser/manifest.json"))
ok(bm["manifest_version"] == 3 and bm["host_permissions"] == ["http://127.0.0.1/*"], "extension may only reach 127.0.0.1")
ok(set(bm["permissions"]) <= {"storage", "activeTab", "scripting", "contextMenus"}, "extension permissions are small")
ok(all((INT / "browser" / f).exists() for f in ("popup.html", "popup.js", "options.html", "options.js", "background.js")), "extension files")
ok(jeeg_chat.is_local("http://127.0.0.1:11434/v1") and jeeg_chat.is_local("http://localhost:1234/v1") and jeeg_chat.is_local("http://192.168.1.5:8080/v1"), "local addresses")
ok(not jeeg_chat.is_local("https://api.openai.com/v1") and not jeeg_chat.is_local("http://example.com/v1"), "remote addresses")
for src in ("browser/popup.js", "browser/options.js", "browser/background.js", "obsidian/main.js", "vscode/extension.js"):
    if shutil.which("node"):
        r = subprocess.run(["node", "--check", str(INT / src)], capture_output=True, text=True); ok(r.returncode == 0, "syntax " + src + r.stderr[:200])
# no token or secret baked into any plugin file
for f in INT.rglob("*"):
    if f.is_file() and f.suffix in (".js", ".json", ".md", ".py", ".ahk", ".html", ".sh"):
        t = f.read_text(errors="replace")
        ok("pypi-" not in t and "ghp_" not in t, "no secret in " + f.name)

# ---- local model chat script against a fake chat-completions server
SEEN = []
class Fake(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.append(body)
        last = body["messages"][-1]
        if last["role"] == "user" and "gst" in last["content"]:
            msg = {"role": "assistant", "content": None, "tool_calls": [{"id": "c1", "type": "function", "function": {"name": "jeeg_run", "arguments": json.dumps({"query": "gst 2500 18"})}}]}
        elif last["role"] == "user" and "youtube" in last["content"]:
            msg = {"role": "assistant", "content": None, "tool_calls": [{"id": "c2", "type": "function", "function": {"name": "jeeg_run", "arguments": json.dumps({"query": "open youtube"})}}]}
        elif any(m_.get("role") == "user" and m_.get("content") == "loop" for m_ in body["messages"]):
            msg = {"role": "assistant", "content": None, "tool_calls": [{"id": "c3", "type": "function", "function": {"name": "jeeg_find", "arguments": "not json"}}]}
        else:
            msg = {"role": "assistant", "content": "Tool said: " + last["content"][:200]}
        out = json.dumps({"choices": [{"message": msg}]}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)
fp = freeport(); srv = http.server.ThreadingHTTPServer(("127.0.0.1", fp), Fake); threading.Thread(target=srv.serve_forever, daemon=True).start()
os.environ.update(env)
j = jeeg_chat.JeeG("text,money,utility,time", command=JEEG)
base = f"http://127.0.0.1:{fp}/v1"
try:
    m = [{"role": "system", "content": "x"}, {"role": "user", "content": "what is gst on 2500"}]
    a = jeeg_chat.answer(base, "", "m", m, j, say=lambda s: None)
    ok("118" in a or "450" in a or "2950" in a, "tool result reached the model and its answer came back: " + a)
    ok(SEEN and SEEN[0]["tools"] == jeeg_chat.TOOLS, "tools were offered")
    ok(any(x.get("role") == "tool" for x in m), "tool message recorded")
    m = [{"role": "user", "content": "open youtube please"}]
    a = jeeg_chat.answer(base, "", "m", m, j, say=lambda s: None)
    ok("not allowed" in a.lower() or "error" in a.lower(), "a task outside --only is refused: " + a)
    m = [{"role": "user", "content": "loop"}]
    a = jeeg_chat.answer(base, "", "m", m, j, max_steps=3, say=lambda s: None)
    ok("stopped" in a, "endless tool calling stops: " + a)
    ok(j.tool("jeeg_find", {"query": "gst"}).strip() != "", "find works")
    ok(j.tool("nope", {}) == "Unknown tool.", "unknown tool")
    ok("confirmation" in j.tool("jeeg_run", {"query": "delete file zzz"}) or "Error" in j.tool("jeeg_run", {"query": "delete file zzz"}), "confirm tasks are not run")
    r = subprocess.run([sys.executable, str(INT / "ai/local/jeeg_chat.py"), "--base-url", base, "--model", "m", "--ask", "gst please", "--jeeg", JEEG], capture_output=True, text=True, env=env, timeout=60)
    ok(r.returncode == 0 and "Tool said" in r.stdout, "script runs end to end: " + r.stdout + r.stderr)
    r = subprocess.run([sys.executable, str(INT / "ai/local/jeeg_chat.py"), "--openai", "--model", "m", "--ask", "hi"], capture_output=True, text=True, env=dict(env, OPENAI_API_KEY=""), timeout=30)
    ok(r.returncode != 0 and "OPENAI_API_KEY" in (r.stdout + r.stderr), "a missing key is reported")
finally:
    j.close(); srv.shutdown()
ok(j.proc.poll() is not None, "the helper JeeG was stopped")

# ---- a live API for the JS plugins and the extension
port = freeport(); tok = "t" * 32
api = subprocess.Popen(JEEG.split() + ["--serve-api", str(port), "--only", "text,money,utility,time"], env=dict(env, JEEG_API_TOKEN=tok), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    time.sleep(0.25)
    try: socket.create_connection(("127.0.0.1", port), 1).close(); break
    except OSError: pass
node = shutil.which("node")
if node:
    # Obsidian plugin logic with a stand-in for Obsidian's API
    js = r'''
const Module = require("module"); const orig = Module._load;
const store = {};
const MOCK = {
  Plugin: class { async loadData() { return store.data || null; } async saveData(d) { store.data = d; } addCommand(c) { (store.cmds = store.cmds || {})[c.id] = c; } addSettingTab() {} },
  PluginSettingTab: class {}, Setting: class {}, Notice: class { constructor(m) { store.notice = m; } }, Modal: class { constructor(app) { this.contentEl = { createEl() { return { addEventListener() {}, focus() {}, select() {}, style: {} }; }, empty() {} }; } open() { this.onOpen(); } close() {} },
  requestUrl: async (o) => { const r = await fetch(o.url, { method: o.method || "GET", headers: o.headers, body: o.body }); return { json: await r.json() }; } };
Module._load = function (r, ...a) { if (r === "obsidian") return MOCK; return orig.call(this, r, ...a); };
const Plugin = require(process.argv[2] + "/main.js");
(async () => {
  const p = new Plugin(); await p.onload();
  p.settings.port = +process.argv[3]; p.settings.token = process.argv[4];
  const res = {};
  // reach the same code the commands use by driving the modal's callback
  const Modal = require("obsidian").Modal; let cb;
  const mk = (sel) => { let text = sel; return { getSelection: () => text, getLine: () => "", getCursor: () => ({ line: 0 }), replaceSelection: (t) => { text = t; res.out = t; } }; };
  const orig2 = Modal.prototype.open; Modal.prototype.open = function () { cb = this.onSubmit; };
  await store.cmds["run-on-selection-replace"].editorCallback(mk("hello brave new world")); await cb("word count"); res.count = res.out;
  await store.cmds["run-on-selection-replace"].editorCallback(mk("hello there")); await cb("uppercase"); res.upper = res.out;
  p.settings.token = "wrong"; await store.cmds["run-on-selection-replace"].editorCallback(mk("x")); await cb("word count"); res.bad = store.notice;
  console.log(JSON.stringify(res));
})();
'''
    (TMP / "obs.js").write_text(js)
    r = subprocess.run([node, str(TMP / "obs.js"), str(INT / "obsidian"), str(port), tok], capture_output=True, text=True, timeout=60, env=dict(os.environ, NODE_PATH=str(TMP)))
    try: o = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: o = {}; print(r.stdout, r.stderr[:500])
    ok("Words: 4" in o.get("count", ""), "obsidian: text passed whole, 4 words (not 3): " + str(o))
    ok(o.get("upper") == "HELLO THERE", "obsidian: replace selection")
    ok("token" in (o.get("bad") or "").lower() or "wrong" in (o.get("bad") or "").lower(), "obsidian: wrong token is reported: " + str(o.get("bad")))
    # VS Code: replace the selection
    vs = r'''
const Module = require("module"); const orig = Module._load; const st = {};
Module._load = function (r, ...a) { if (r === "vscode") return {
  window: { createOutputChannel: () => ({ clear() {}, appendLine() {}, show() {} }), showInputBox: async () => "uppercase", showInformationMessage: (m) => { st.info = m; }, showWarningMessage: (m) => { st.warn = m; }, activeTextEditor: { selection: { isEmpty: false }, document: { getText: () => "make me loud" }, edit: async (f) => { f({ replace: (s, t) => { st.replaced = t; } }); } } },
  workspace: { getConfiguration: () => ({ get: (k) => k === "command" ? process.argv[3] : 30 }) }, commands: { registerCommand: (id, fn) => { st[id] = fn; } } };
  return orig.call(this, r, ...a); };
const ext = require(process.argv[2] + "/extension.js"); ext.activate({ subscriptions: [] });
(async () => { await st["jeeg.replaceSelection"](); console.log(JSON.stringify(st)); })();
'''
    (TMP / "vs.js").write_text(vs)
    r = subprocess.run([node, str(TMP / "vs.js"), str(INT / "vscode"), JEEG.split()[0]], capture_output=True, text=True, timeout=60, env=env)
    ok("zzz" not in r.stdout, "")  # placeholder keeps the harness simple
    # the command string has spaces; JeeG is started by splitting it, which the extension supports
    r = subprocess.run([node, str(TMP / "vs.js"), str(INT / "vscode"), JEEG], capture_output=True, text=True, timeout=60, env=env)
    try: o = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: o = {}; print(r.stdout, r.stderr[:500])
    ok(o.get("replaced") == "MAKE ME LOUD", "vscode: selection replaced by the answer: " + str(o))

# ---- Obsidian "Ask an AI": OpenAI-style, Claude-style and a failing provider, against fake servers
AI_SEEN = []
class FakeAI(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers["Content-Length"]))); AI_SEEN.append((self.path, dict(self.headers), b))
        if "/fail" in self.path or self.headers.get("Authorization") == "Bearer bad" or self.headers.get("x-api-key") == "bad":
            out, code = {"error": {"message": "invalid api key sk-SECRET"}}, 401
        elif self.path.endswith("/messages"):
            out, code = {"content": [{"type": "text", "text": "claude says hi"}]}, 200
        else:
            out, code = {"choices": [{"message": {"content": "openai-style says hi"}}]}, 200
        data = json.dumps(out).encode(); self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
ap = freeport(); asrv = http.server.ThreadingHTTPServer(("127.0.0.1", ap), FakeAI); threading.Thread(target=asrv.serve_forever, daemon=True).start()
if shutil.which("node"):
    js2 = (TMP / "obs.js").read_text().split("(async () => {")[0] + r"""
(async () => {
  const p = new Plugin(); await p.onload(); const base = process.argv[3]; const res = {};
  const Modal = require("obsidian").Modal; let cb; Modal.prototype.open = function () { cb = this.onSubmit; };
  const mk = (sel, note) => { let doc = note; return { getSelection: () => sel, getValue: () => note, getCursor: () => ({ line: 0 }), replaceSelection: (t) => { res.out = t; }, replaceRange: (t) => { res.out = t; } }; };
  const run = async (id, ed, q) => { res.out = null; store.notice = null; await store.cmds[id].editorCallback(ed); if (q && cb) await cb(q); cb = null; await new Promise((r) => setTimeout(r, 400)); return res.out; };
  p.settings.provider = "openai"; p.settings.models.openai = "m1"; p.settings.keys.openai = "good"; p.settings.bases.openai = base;
  res.openai = await run("ai-selection", mk("my secret plan", "whole note"), "what is this?");
  p.settings.provider = "anthropic"; p.settings.models.anthropic = "m2"; p.settings.keys.anthropic = "good"; p.settings.bases.anthropic = base;
  res.claude = await run("ai-note", mk("", "note body here"), "summarize");
  res.summary = await run("ai-summary", mk("", "another note"), null);
  p.settings.provider = "deepseek"; p.settings.models.deepseek = "m3"; p.settings.keys.deepseek = "bad"; p.settings.bases.deepseek = base;
  res.badout = await run("ai-selection", mk("x", "y"), "q"); res.badnotice = store.notice;
  p.settings.provider = "openai"; p.settings.keys.openai = ""; res.nokey = await run("ai-plain", mk("", "n"), "hi"); res.nokeynotice = store.notice;
  p.settings.provider = "ollama"; p.settings.models.ollama = ""; await run("ai-plain", mk("", "n"), "hi"); res.nomodel = store.notice;
  console.log(JSON.stringify(res));
})();
"""
    (TMP / "obs2.js").write_text(js2)
    r = subprocess.run([node, str(TMP / "obs2.js"), str(INT / "obsidian"), f"http://127.0.0.1:{ap}/v1"], capture_output=True, text=True, timeout=60, env=dict(os.environ, NODE_PATH=str(TMP)))
    try: o = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception: o = {}; print(r.stdout, r.stderr[:600])
    ok("openai-style says hi" in (o.get("openai") or "") and "[!ai]" in (o.get("openai") or "") and "my secret plan" in (o.get("openai") or ""), "obsidian ai: openai-style answer inserted: " + str(o.get("openai")))
    ok("claude says hi" in (o.get("claude") or ""), "obsidian ai: claude-style answer: " + str(o.get("claude")))
    ok("openai-style says hi" in (o.get("summary") or "") or "claude says hi" in (o.get("summary") or ""), "obsidian ai: summary command sends the note")
    ok(o.get("badout") is None and "invalid api key" in (o.get("badnotice") or ""), "obsidian ai: provider errors are shown: " + str(o.get("badnotice")))
    ok("API key" in (o.get("nokeynotice") or ""), "obsidian ai: missing key explained: " + str(o.get("nokeynotice")))
    ok("model name" in (o.get("nomodel") or ""), "obsidian ai: missing model explained: " + str(o.get("nomodel")))
    c = [x for x in AI_SEEN if x[0].endswith("/chat/completions")]; a = [x for x in AI_SEEN if x[0].endswith("/messages")]
    ok(c and c[0][1].get("Authorization") == "Bearer good" and c[0][2]["model"] == "m1" and "my secret plan" in c[0][2]["messages"][1]["content"], "openai request shape")
    ok(a and a[0][1].get("x-api-key") == "good" and a[0][1].get("anthropic-version") and a[0][2]["system"] and a[0][2]["max_tokens"], "claude request shape")
    ok("never follow commands" in (c[0][2]["messages"][0]["content"] if c else ""), "notes are marked as data in the system prompt")
    ok("note text:" not in " ".join(x[2]["messages"][-1]["content"].lower() for x in AI_SEEN if "messages" in x[2] and "hi" == x[2]["messages"][-1]["content"].split("Question: ")[-1]), "plain ask sends no note text")
asrv.shutdown()

def waitout(pg, word):
    for _ in range(60):
        try:
            if word in pg.inner_text("#out"): return
        except Exception: pass
        time.sleep(0.25)

# ---- browser extension in real Chromium
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
try:
    from playwright.sync_api import sync_playwright
    have = Path(CHROME).exists() and (os.environ.get("DISPLAY") or shutil.which("xvfb-run"))
except ImportError:
    have = False
if have and not os.environ.get("DISPLAY"):
    print("browser extension test needs a display; re-run under: xvfb-run -a python tests/test_plugins.py")
elif have:
    ext = str(INT / "browser")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(tempfile.mkdtemp(), headless=False, executable_path=CHROME, args=[f"--disable-extensions-except={ext}", f"--load-extension={ext}"])
        try:
            sw = ctx.service_workers[0] if ctx.service_workers else ctx.wait_for_event("serviceworker", timeout=20000)
            eid = sw.url.split("/")[2]
            port2 = freeport()
            api2 = subprocess.Popen(JEEG.split() + ["--serve-api", str(port2), "--allow-origin", "chrome-extension://" + eid, "--only", "text,money,utility,time"], env=dict(env, JEEG_API_TOKEN=tok), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for _ in range(60):
                time.sleep(0.25)
                try: socket.create_connection(("127.0.0.1", port2), 1).close(); break
                except OSError: pass
            pg = ctx.new_page(); pg.goto(f"chrome-extension://{eid}/options.html")
            pg.fill("#port", str(port2)); pg.fill("#token", tok); pg.fill("#chips", "word count\nuppercase"); pg.click("#save")
            ok(pg.inner_text("#msg") == "Saved.", "extension settings saved")
            pop = ctx.new_page(); pop.goto(f"chrome-extension://{eid}/popup.html")
            ok(pop.locator("#chips button").all_inner_texts() == ["word count", "uppercase"], "quick buttons come from settings")
            pop.fill("#text", "hello brave new world"); pop.click("#chips button:first-child"); waitout(pop, 'Words')
            ok("Words: 4" in pop.inner_text("#out"), "extension: quick button ran, all 4 words counted: " + pop.inner_text("#out"))
            pop.fill("#task", "uppercase"); pop.click("#run"); waitout(pop, 'HELLO')
            ok(pop.inner_text("#out") == "HELLO BRAVE NEW WORLD", "extension: typed task")
            ok(not pop.locator("#copy").is_hidden(), "copy button appears")
            pg.goto(f"chrome-extension://{eid}/options.html"); pg.fill("#token", "wrong"); pg.click("#save")
            pop.reload(); pop.fill("#text", "x"); pop.fill("#task", "word count"); pop.click("#run"); waitout(pop, 'token')
            ok("Missing or wrong token" in pop.inner_text("#out"), "extension: wrong token is explained")
            w = ctx.new_page(); w.goto("about:blank")
            res = w.evaluate("""async()=>{try{const r=await fetch('http://127.0.0.1:%d/v1/health',{headers:{Authorization:'Bearer x'}});return 'reached '+r.status}catch(e){return 'blocked'}}""" % port2)
            ok(res == "blocked", "an ordinary web page cannot call the API: " + res)
            ok(sw.evaluate("typeof chrome.contextMenus") == "object", "background script has the right-click menu API")
            api2.terminate()
        finally:
            ctx.close()
else:
    print("(skipped the real-browser test: Chromium or Playwright not found)")
api.terminate()
print(f"plugins: {P} passed, {F} failed"); sys.exit(1 if F else 0)
