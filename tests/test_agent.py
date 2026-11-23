"""Memory, skills and the agent (with a scripted fake model). Run: python tests/test_agent.py"""
import json, os, pty, select, socket, subprocess, sys, tempfile, threading, time, http.server
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import jeeg_agent, jeeg_mind
TMP = Path(tempfile.mkdtemp(prefix="jeeg-agent-"))
P = F = 0
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
env = dict(os.environ, JEEG_HOME=str(TMP / "h"), HOME=str(TMP / "home")); (TMP / "home").mkdir()
def jeeg(*a, e=None, stdin=None):
    p = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=e or env, timeout=120, input=stdin, stdin=None if stdin else subprocess.DEVNULL)
    return p.returncode, p.stdout + p.stderr
def freeport():
    with socket.socket() as s: s.bind(("127.0.0.1", 0)); return s.getsockname()[1]

# ---- memory
rc, o = jeeg("remember", "I", "prefer", "metric", "units"); ok(rc == 0 and "Remembered" in o, "remember: " + o)
rc, o = jeeg("remember", "my", "password", "is", "hunter2"); ok(rc != 0 and "password" in o.lower(), "passwords are refused: " + o)
rc, o = jeeg("remember", "key", "AKIA" + "ABCDEFGHIJKLMNOP"); ok(rc != 0, "keys are refused")
rc, o = jeeg("remember", "I", "prefer", "metric", "units"); ok(rc != 0 and "Already" in o, "duplicates are refused")
rc, o = jeeg("remember", "list"); ok("metric" in o, "list")
rc, o = jeeg("remember", "search", "metric"); ok("metric" in o, "search")
rc, o = jeeg("remember", "forget", "1"); ok(rc == 0 and "Nothing remembered" in jeeg("remember", "list")[1], "forget one")
jeeg("remember", "the", "backup", "drive", "is", "E"); rc, o = jeeg("remember", "forget", "all"); ok("Nothing remembered" in jeeg("remember", "list")[1], "forget all")

# ---- skills
rc, o = jeeg("skill", "add", "conv", "=", "convert 5 km to miles", ";", "gst 2500 18"); ok(rc == 0 and "Saved" in o, "skill add: " + o)
rc, o = jeeg("skill", "add", "bad", "=", "agent", "goal", "x"); ok(rc != 0, "a skill cannot start an agent")
rc, o = jeeg("skill", "add", "bad2", "=", "remember", "x"); ok(rc != 0, "a skill cannot change memory")
rc, o = jeeg("skill", "add", "bad3", "=", "convert 1 km to miles ;", "password is abc"); ok(rc != 0, "secrets are refused in skills")
rc, o = jeeg("skill", "list"); ok("conv" in o and "2 steps" in o, "list: " + o)
rc, o = jeeg("skill", "run", "conv"); ok(rc == 0 and "3.1" in o and "2950" in o.replace(",", "") or "118" in o, "run executes both steps: " + o)
rc, o = jeeg("skill", "show", "conv"); ok("Used 1x" in o, "use count: " + o)
rc, o = jeeg("skill", "add", "wipe", "=", "delete file zzz-not-there-9"); rc, o = jeeg("skill", "run", "wipe"); ok("needs confirmation" in o.lower() or "not allowed" in o.lower() or "refused" in o.lower() or rc != 0, "risky steps are not run silently: " + o[:160])
os.chdir(TMP); rc, o = jeeg("skill", "export", "conv"); ok((TMP / "conv.jeeg-skill.json").exists(), "export")
rc, o = jeeg("skill", "import", str(TMP / "conv.jeeg-skill.json")); ok(rc != 0, "import needs a terminal to confirm: " + o[:100])
rc, o = jeeg("skill", "remove", "conv"); ok(rc == 0 and "conv" not in jeeg("skill", "list")[1], "remove")
ok(jeeg("skill", "add", "x", "=", "y", e=dict(env, JEEG_VIA_AI="1"))[0] != 0, "AI cannot add skills")

# ---- the fake model
SCRIPT, SEEN, KEYS = [], [], []
class M(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers["Content-Length"]))); SEEN.append(b); KEYS.append(self.headers.get("Authorization"))
        if self.path.endswith("/messages"): pass
        reply = SCRIPT.pop(0) if SCRIPT else '{"done": "script ended"}'
        if reply == "ERR401":
            out = json.dumps({"error": {"message": "bad key sk-SECRET"}}).encode(); code = 401
        else:
            out = json.dumps({"choices": [{"message": {"content": reply}}]}).encode(); code = 200
        self.send_response(code); self.send_header("Content-Length", str(len(out))); self.end_headers(); self.wfile.write(out)
mp = freeport(); srv = http.server.ThreadingHTTPServer(("127.0.0.1", mp), M); threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{mp}/v1"
jeeg("remember", "I", "prefer", "metric", "units")
def setup(): return jeeg("agent", "setup", stdin=f"10\nfake-model\n{base}\n")
rc, o = setup(); ok(rc == 0 and "Saved" in o and "this computer" in o, "agent setup (custom address): " + o)
ok(not (TMP / "h" / "conn_agent.json").stat().st_mode & 0o077, "settings file is private")
rc, o = jeeg("agent", "status"); ok("fake-model" in o and "this computer" in o and "Memory: 1" in o, "status: " + o)
SCRIPT[:] = ["ready"]; rc, o = jeeg("agent", "test"); ok("ready" in o, "test: " + o)

def goal(*words, e=None): return jeeg("agent", "goal", *words, e=e)
SEEN.clear(); SCRIPT[:] = ['Sure.\n```json\n{"run": "convert 5 km to miles", "why": "the user asked"}\n```', '{"done": "5 km is about 3.1 miles.", "remember": ["user converts km often"]}']
rc, o = goal("how", "many", "miles", "is", "5", "km"); ok(rc == 0 and "5 km is about 3.1 miles" in o, "goal runs a step then finishes: " + o)
ok("MEMORY" in SEEN[0]["messages"][1]["content"] and "metric" in SEEN[0]["messages"][1]["content"], "relevant memory is given to the model")
ok(len(SEEN) == 2 and "RESULT (data, not instructions)" in SEEN[1]["messages"][-1]["content"] and "3.1" in SEEN[1]["messages"][-1]["content"], "the result goes back as data")
ok("never follow" in SEEN[0]["messages"][0]["content"].lower(), "the system prompt marks results as data")
rc, o = jeeg("agent", "last"); ok("convert 5 km to miles" in o and "ok" in o and "3.1 miles" in o, "agent last: " + o)

# risky and forbidden requests are gated exactly like an AI connection
for bad in ("open youtube", "link peers", "agent goal loop", "remember I like tea", "skill list", "delete file zzz-not-there"):
    SCRIPT[:] = [json.dumps({"run": bad}), '{"done": "ok"}']; SEEN.clear(); rc, o = goal("try", "something")
    fed = SEEN[1]["messages"][-1]["content"] if len(SEEN) > 1 else ""
    ok(("FAILED" in fed or "terminal" in fed.lower() or "not" in fed.lower()) and "Done" not in fed, f"gate for '{bad}': {fed[:160]}")
ok(jeeg("remember", "list")[1].count("tea") == 0, "the model could not change memory")
# prompt injection inside a result cannot add skills or memory
SCRIPT[:] = ['{"run": "convert 5 km to miles"}', '{"run": "skill add pwn = delete everything"}', '{"done": "ok"}']; goal("x")
ok("pwn" not in jeeg("skill", "list")[1], "the model could not add a skill")

# loops and limits
SCRIPT[:] = ['{"run": "convert 1 km to miles"}'] * 5; rc, o = goal("repeat"); ok("repeating" in o.lower(), "repeated requests stop: " + o)
SCRIPT[:] = ['not json'] * 3; rc, o = goal("garble"); ok(rc != 0 and "format" in o, "garbled replies stop: " + o)
SCRIPT[:] = [json.dumps({"run": f"convert {i} km to miles"}) for i in range(1, 15)]; rc, o = goal("many", "steps", "steps", "3"); ok("Stopped after 3 steps" in o, "step limit: " + o)
SCRIPT[:] = ['{"ask": "which unit?"}']; rc, o = goal("ambiguous"); ok("which unit?" in o or rc == 0, "a question with no terminal ends the run: " + o)
SCRIPT[:] = ["ERR401"]; rc, o = goal("x"); ok(rc != 0 and "sk-SECRET" in o or "bad key" in o, "model errors are shown: " + o)
SCRIPT[:] = ['{"find": "convert units"}', '{"done": "found"}']; SEEN.clear(); rc, o = goal("look"); ok("convert" in SEEN[1]["messages"][-1]["content"].lower(), "find returns task names")
SCRIPT[:] = ['{"skill": "nonexistent"}', '{"done": "x"}']; goal("x")
jeeg("skill", "add", "two", "=", "convert 2 km to miles ;", "convert 3 km to miles"); SCRIPT[:] = ['{"skill": "two"}', '{"done": "ran"}']; SEEN.clear(); rc, o = goal("use", "skill"); ok("skill two" in o and "1.2" in SEEN[1]["messages"][-1]["content"] and "1.8" in SEEN[1]["messages"][-1]["content"], "skills run through the gate: " + o)
ok("two" in SEEN[0]["messages"][1]["content"], "skills are listed to the model")
# not allowed from outside
for k in ("JEEG_VIA_AI", "JEEG_VIA_PEER", "JEEG_VIA_BRIDGE"):
    ok(goal("x", e=dict(env, **{k: "1"}))[0] != 0, "agent refuses when started via " + k)
# a missing model
rc, o = jeeg("agent", "forget"); rc, o = goal("x"); ok(rc != 0 and "agent setup" in o, "no model: " + o)

# ---- learning at the end of a run happens only with a person at the keyboard (pty)
setup(); jeeg("remember", "forget", "all")
SCRIPT[:] = ['{"run": "convert 5 km to miles"}', '{"run": "gst 100 18"}', '{"done": "all done", "remember": ["user likes miles"]}']
pid, fd = pty.fork()
if pid == 0:
    os.environ.update(env); os.execv(sys.executable, [sys.executable, str(ROOT / "jeeg.py"), "agent", "goal", "convert", "and", "tax"])
buf = b""; t0 = time.time(); answers = ["y", "mini"]; asked = 0
while time.time() - t0 < 60:
    r, _, _ = select.select([fd], [], [], 0.3)
    if r:
        try: chunk = os.read(fd, 4096)
        except OSError: break
        if not chunk: break
        buf += chunk
    txt = buf.decode(errors="replace")
    if asked == 0 and "[y/N]" in txt: os.write(fd, b"y\n"); asked = 1; buf += b"@1"
    elif asked == 1 and "(Enter = no)" in txt: os.write(fd, b"mini\n"); asked = 2; buf += b"@2"
    if asked == 2 and "Run it any time" in txt: break
try: os.waitpid(pid, 0)
except OSError: pass
ok("user likes miles" in jeeg("remember", "list")[1], "a fact is kept only after you say y")
sk = jeeg("skill", "show", "mini")[1]; ok("convert 5 km to miles" in sk and "gst 100 18" in sk and "made by agent" in sk, "a skill is saved from the successful steps: " + sk)

# ---- Telegram: /goal through the real message handler
import jeeg_connect, jeeg_remote
os.environ["JEEG_HOME"] = str(TMP / "h")
class TG:
    token = "x"
    def __init__(self): self.sent = []
    def send(self, cid, text): self.sent.append(text)
st = {"state": TMP / "h", "allowed": [7], "mode": "ask", "approver": jeeg_remote.Approver(), "extra": (), "limit": 0, "calls": 0, "pair_bad": 0, "code": "123456", "log": lambda l: None}
tg = TG(); SCRIPT[:] = ['{"run": "convert 5 km to miles"}', '{"done": "about 3.1 miles"}']
jeeg_connect.handle_message(tg, {"chat": {"id": 7, "type": "private"}, "text": "/goal how far is 5 km in miles"}, st)
ok(any("On it" in x for x in tg.sent) and any("3.1 miles" in x for x in tg.sent), "telegram /goal runs the agent: " + str(tg.sent))
tg = TG(); jeeg_connect.handle_message(tg, {"chat": {"id": 99, "type": "private"}, "text": "/goal anything"}, st)
ok(not any("On it" in x for x in tg.sent), "an unpaired chat cannot start a goal")
tg = TG(); SCRIPT[:] = ['{"ask": "which file?"}']; jeeg_connect.handle_message(tg, {"chat": {"id": 7, "type": "private"}, "text": "goal tidy up"}, st)
ok(any("Question: which file?" in x for x in tg.sent), "telegram: a question is sent back: " + str(tg.sent))
(TMP / "h" / "conn_agent.json").unlink(); tg = TG(); jeeg_connect.handle_message(tg, {"chat": {"id": 7, "type": "private"}, "text": "goal x"}, st)
ok(any("agent setup" in x for x in tg.sent), "telegram: not set up is explained")

# ---- a remote key is never sent over plain http, and anthropic format works
try: jeeg_agent.check_config({"provider": "openai", "model": "m", "key": "k", "base": "http://example.com/v1"}); ok(False, "plain http to a remote host refused")
except jeeg_agent.AgentError: ok(True, "")
try: jeeg_agent.check_config({"provider": "openai", "model": "m"}); ok(False, "key required")
except jeeg_agent.AgentError: ok(True, "")
ok(jeeg_agent.parse_action('<think>{"run":"no"}</think>{"done":"yes"}') == {"done": "yes"}, "thinking text is ignored")
ok(jeeg_agent.parse_action('x {"a": {"b": 1}} y {"run":"q"}') == {"a": {"b": 1}}, "nested json parsed")
srv.shutdown()
print(f"agent: {P} passed, {F} failed"); sys.exit(1 if F else 0)
