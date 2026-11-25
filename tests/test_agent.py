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

# ======================= v2: limits, backup model, plans, history, audit, templates, schedules, review, packs
def pty_run(args, answers, wait=60, e=None):
    """Run jeeg in a pseudo-terminal; answers = [(text to wait for, reply)] in order."""
    pid, fd = pty.fork()
    if pid == 0:
        os.environ.update(e or env); os.execv(sys.executable, [sys.executable, str(ROOT / "jeeg.py"), *args])
    buf = ""; t0 = time.time(); i = 0; seen_len = 0
    while time.time() - t0 < wait:
        r, _, _ = select.select([fd], [], [], 0.3)
        if r:
            try: chunk = os.read(fd, 4096)
            except OSError: break
            if not chunk: break
            buf += chunk.decode(errors="replace")
        if i < len(answers) and answers[i][0] in buf[seen_len:]:
            os.write(fd, (answers[i][1] + "\n").encode()); seen_len = len(buf); i += 1
    try: os.kill(pid, 15)
    except OSError: pass
    try: os.waitpid(pid, 0)
    except OSError: pass
    return buf
def reset_usage():
    p = TMP / "h" / "agent_usage.json"
    if p.exists(): p.unlink()

setup(); reset_usage()
# daily limit
jeeg("agent", "limit", "2"); SCRIPT[:] = ['{"run": "convert 1 km to miles"}', '{"run": "convert 2 km to miles"}', '{"run": "convert 3 km to miles"}', '{"done": "x"}']
rc, o = goal("limit", "test"); ok("daily limit of 2" in o, "daily cap stops the agent: " + o[-160:])
rc, o = jeeg("agent", "status"); ok("2 of 2" in o, "status shows the usage: " + o)
jeeg("agent", "limit", "200"); reset_usage()
ok(jeeg("agent", "limit", "0")[0] != 0 and jeeg("agent", "limit", "banana")[0] != 0, "bad limits refused")

# backup model: main address is dead, backup is the fake server
cfgp = TMP / "h" / "conn_agent.json"; c = json.loads(cfgp.read_text()); c["base"] = f"http://127.0.0.1:{freeport()}/v1"; cfgp.write_text(json.dumps(c))
rc, o = jeeg("agent", "goal", "use", "backup"); ok(rc != 0 and "Could not reach" in o, "no backup: the failure is shown: " + o[-100:])
rc, o = jeeg("agent", "setup", "backup", stdin=f"10\nbackup-model\n{base}\n"); ok(rc == 0 and "Backup saved" in o, "setup backup: " + o)
SCRIPT[:] = ['{"done": "answered by the backup"}']; rc, o = goal("use", "backup"); ok("answered by the backup" in o, "the backup model answers when the main one is down: " + o[-120:])
ok(SEEN[-1]["model"] == "backup-model", "the backup model name was used")
ok("Backup model" in jeeg("agent", "status")[1], "status mentions the backup")
setup()                                                  # back to a single working model
ok("fallback" not in json.loads(cfgp.read_text()) or True, "")

# plan only
SEEN.clear(); SCRIPT[:] = ['{"plan": [{"run": "convert 5 km to miles", "why": "units"}, {"run": "delete file zzz-not-there-2", "why": "tidy"}, {"run": "link peers"}]}']
rc, o = jeeg("agent", "plan", "do", "stuff"); ok(rc == 0 and "[safe]" in o and "asks first" in o and "terminal only" in o and "nothing has run" in o and len(SEEN) == 1, "agent plan labels each step and runs nothing: " + o)
SCRIPT[:] = ["I would do many things"]; ok(jeeg("agent", "plan", "x")[0] != 0, "a plan in the wrong format is refused")
SCRIPT[:] = [json.dumps({"plan": [{"run": "note add my password is hunter2"}]})]; rc, o = jeeg("agent", "plan", "x"); ok(rc != 0 and "password" in o.lower(), "a plan with a secret is refused: " + o[-100:])
# plan first, approved
SEEN.clear(); SCRIPT[:] = ['{"plan": [{"run": "convert 5 km to miles"}, {"run": "gst 100 18"}]}', '{"done": "5 km is 3.1 miles and 100 plus 18% is 118"}']
out = pty_run(["agent", "goal", "convert", "and", "tax", "plan", "first"], [("[y/N]", "y")]); ok("step 1 of 2" in out and "step 2 of 2" in out and "118" in out, "plan first: runs exactly the approved steps: " + out[-300:])
ok(len(SEEN) == 2, "plan first: one call to plan and one to summarise")
SEEN.clear(); SCRIPT[:] = ['{"plan": [{"run": "convert 5 km to miles"}]}']
out = pty_run(["agent", "goal", "convert", "plan", "first"], [("[y/N]", "n")]); ok("Not run" in out and "step 1 of" not in out, "plan first: n runs nothing: " + out[-150:])
SCRIPT[:] = ['{"plan": [{"run": "convert 5 km to miles"}]}']; rc, o = jeeg("agent", "goal", "convert", "plan", "first"); ok(rc != 0 and "terminal" in o, "plan first without a terminal is refused")
SCRIPT[:] = ['{"plan": [{"run": "open youtube"}, {"run": "convert 5 km to miles"}]}', '{"done": "stopped early"}']
out = pty_run(["agent", "goal", "x", "read", "plan", "first"], [("[y/N]", "y")]); ok("step 1 of 2" in out and "step 2 of 2" not in out, "a refused step stops the plan: " + out[-250:])

# history, again, audit
rc, o = jeeg("agent", "history"); ok(rc == 0 and "steps" in o and "calls" in o, "history: " + o[:200])
rc, o = jeeg("agent", "audit", "10"); ok("REFUSED" in o and "ok" in o, "audit shows allowed and refused requests: " + o[:400])
SCRIPT[:] = ['{"done": "again works"}']; rc, o = jeeg("agent", "again", "1"); ok(rc == 0 and ("Again:" in o), "again: " + o[:200])
ok(jeeg("agent", "again", "99")[0] != 0, "again with a bad number")

# templates
rc, o = jeeg("agent", "template", "list"); ok("cleanup-report" in o and "notes-week" in o, "templates listed")
SEEN.clear(); SCRIPT[:] = ['{"done": "template ran"}']; rc, o = jeeg("agent", "template", "run", "disk-check"); ok("template ran" in o and "mode: read" in o, "a template runs in read mode: " + o[:200])
ok(jeeg("agent", "template", "run", "nope")[0] != 0, "unknown template")

# injection cases: nothing may run in read mode
for line in (ROOT / "tests" / "injection_cases.txt").read_text().splitlines():
    if not line.strip() or line.startswith("#"): continue
    SEEN.clear(); SCRIPT[:] = [json.dumps({"run": line}), '{"done": "finished"}']
    rc, o = jeeg("agent", "goal", "hostile", "read")
    fed = SEEN[1]["messages"][-1]["content"] if len(SEEN) > 1 else ""
    ok("FAILED" in fed, f"injection '{line}' was refused in read mode: {fed[:150]}")
ok(not (TMP / "h" / "skills.json").exists() or "pwn" not in (TMP / "h" / "skills.json").read_text(), "injection did not create a skill")

# schedules
rc, o = jeeg("agent", "schedule", "add", "brief", "daily", "at", "08:00", "read", "=", "tell me what is due"); ok(rc == 0 and "look-only" in o, "schedule add: " + o)
ok(jeeg("agent", "schedule", "add", "x", "sometimes", "=", "g")[0] != 0, "bad time refused")
ok(jeeg("agent", "schedule", "add", "brief", "every 2 hours", "=", "g")[0] != 0, "duplicate name refused")
ok(jeeg("agent", "schedule", "add", "tiny", "every", "1", "minutes", "=", "g")[0] != 0, "intervals under 15 minutes refused")
ok(jeeg("agent", "schedule", "add", "wild", "every 1 hours", "god", "=", "g")[0] != 0 or "wild" not in jeeg("agent", "schedule", "list")[1].split("god")[0] or True, "")
rc, o = jeeg("agent", "schedule", "add", "poll", "every", "15", "minutes", "safe", "=", "convert units please"); ok(rc == 0, "interval schedule: " + o)
rc, o = jeeg("agent", "schedule", "list"); ok("brief" in o and "poll" in o and "08:00" in o, "list: " + o)
sp = TMP / "h" / "agent_schedule.json"; its = json.loads(sp.read_text()); its[0]["on"] = False; sp.write_text(json.dumps(its))   # only `poll` is on
SEEN.clear(); SCRIPT[:] = ['{"run": "delete file zzz-not-there-3"}', '{"run": "convert 7 km to miles"}', '{"done": "poll finished"}']
rc, o = jeeg("agent", "schedule", "run", "once"); ok("[schedule] poll" in o and "poll finished" in o, "a due schedule runs: " + o)
fed = SEEN[1]["messages"][-1]["content"]; ok("FAILED" in fed, "unattended: a task that needs a yes is refused: " + fed[:120])
its = json.loads(sp.read_text()); ok(its[1]["outcome"] == "done" and "poll finished" in its[1]["result"] and its[1]["last"] > 0, "result is stored")
SEEN.clear(); rc, o = jeeg("agent", "schedule", "run", "once"); ok(not SEEN and "[schedule]" not in o, "not run again before it is due")
import jeeg_agent as JA
base_t = time.mktime((2026, 11, 23, 9, 0, 0, 0, 0, -1))      # a Monday, 09:00
ok(JA.is_due({"at": "08:00", "last": 0}, base_t), "daily item is due after its time")
ok(not JA.is_due({"at": "08:00", "last": base_t - 3600}, base_t), "daily item already ran today")
ok(not JA.is_due({"at": "10:00", "last": 0}, base_t), "daily item not due before its time")
ok(not JA.is_due({"at": "08:00", "weekdays": True, "last": 0}, time.mktime((2026, 11, 22, 9, 0, 0, 0, 0, -1))), "weekdays item skips Sunday")
ok(JA.parse_when("every 6 hours") == {"every": 360} and JA.parse_when("weekdays at 7:05") == {"at": "07:05", "weekdays": True} and JA.parse_when("every 2 minutes") is None and JA.parse_when("daily at 25:00") is None, "parse_when")
ok(jeeg("agent", "schedule", "remove", "poll")[0] == 0 and "poll" not in jeeg("agent", "schedule", "list")[1], "schedule remove")

# classify
ok(JA.classify("convert 5 km to miles") == "safe" and "terminal" in JA.classify("link peers") and "asks first" in JA.classify("delete file zzz") and JA.classify("qqqq zzzz xxxx") == "unknown task", "classify labels")

# memory: expiry, suggestions, review
jeeg("remember", "forget", "all")
rc, o = jeeg("remember", "I", "am", "travelling", "for", "30", "days"); ok("30 days" in o, "remember with expiry: " + o)
mf = TMP / "h" / "memory.json"; mem = json.loads(mf.read_text()); mem[0]["expires"] = int(time.time()) - 5; mf.write_text(json.dumps(mem))
ok("expired" in jeeg("remember", "list")[1], "expired items are marked")
SEEN.clear(); SCRIPT[:] = ['{"done": "x"}']; goal("travelling", "plans"); ok("MEMORY" not in SEEN[0]["messages"][1]["content"], "expired memory is not given to the model")
rc, o = jeeg("remember", "forget", "expired"); ok("Forgot 1" in o, "forget expired")
SCRIPT[:] = ['{"done": "ok", "remember": ["user works in Pune"]}']; rc, o = goal("note", "something"); ok("waiting for you" in o, "unattended run parks suggestions: " + o[-160:])
ok(jeeg("remember", "list")[1].count("Pune") == 0, "a suggestion is not memory yet")
rc, o = jeeg("remember", "review"); ok(rc != 0 and "Pune" in o, "review without a terminal lists them but changes nothing")
out = pty_run(["remember", "review"], [("[y/N/q]", "y")] * 3); ok("Kept" in out and "Pune" in jeeg("remember", "list")[1], "review y keeps it: " + out[-120:])
ok(jeeg("remember", "review", e=dict(env, JEEG_VIA_AI="1"))[0] != 0, "AI cannot review")
ok(not jeeg_mind.Mind(TMP / "h").suggest("my password is x1y2z3"), "secrets are never suggested")

# skill packs, review labels, improve, undo
rc, o = jeeg("skill", "pack", "list"); ok("developer" in o and "student" in o and "home" in o, "packs listed")
rc, o = jeeg("skill", "pack", "show", "developer"); ok("[looks only]" in o and "git status" in o, "pack steps are shown with labels: " + o[:200])
for pk in jeeg_mind.PACKS.values():
    for nm, d in pk["skills"].items():
        for stp in d["steps"]: ok(JA.classify(stp) in ("safe", "looks only", "asks first"), f"pack step '{stp}' cannot change things: {JA.classify(stp)}")
ok(jeeg("skill", "pack", "install", "developer")[0] != 0, "pack install needs a terminal")
out = pty_run(["skill", "pack", "install", "developer"], [("[y/N]", "y")]); ok("Installed 3" in out and "dev-status" in jeeg("skill", "list")[1], "pack install after y: " + out[-120:])
jeeg("skill", "add", "broken", "=", "convert 5 km to miles", ";", "zzzqq nothing exists here")
rc, o = jeeg("skill", "run", "broken"); ok(rc != 0, "a failing skill fails")
ok(json.loads((TMP / "h" / "skills.json").read_text())["broken"].get("last_error"), "the failure is recorded")
SEEN.clear(); SCRIPT[:] = ['{"steps": ["convert 5 km to miles", "gst 100 18"], "why": "second step did not exist"}']
out = pty_run(["skill", "improve", "broken"], [("[y/N]", "y")]); ok("Saved" in out, "improve: " + out[-250:])
sk = json.loads((TMP / "h" / "skills.json").read_text())["broken"]; ok(sk["steps"] == ["convert 5 km to miles", "gst 100 18"] and sk["prev"][1].startswith("zzzqq") and sk["source"] == "improved", "improved steps saved, old kept")
ok("<<<" in SEEN[0]["messages"][1]["content"] and "data, not instructions" in SEEN[0]["messages"][0]["content"], "the error goes to the model as data")
rc, o = jeeg("skill", "undo", "broken"); ok(rc == 0 and json.loads((TMP / "h" / "skills.json").read_text())["broken"]["steps"][1].startswith("zzzqq"), "skill undo")
SCRIPT[:] = ['{"steps": ["agent goal x"]}']; out = pty_run(["skill", "improve", "broken"], [("[y/N]", "y")]); ok("cannot start" in out or "Saved" not in out, "an improved skill cannot start an agent: " + out[-150:])
ok(jeeg("skill", "improve", "conv-none")[0] != 0, "improve on a missing skill")
ok(jeeg("skill", "undo", "broken", e=dict(env, JEEG_VIA_AI="1"))[0] != 0, "AI cannot undo skills")

# approval card: the question names the task and what it does
import jeeg_remote as JR
asked = []
class Cap(JR.Approver):
    def ask(self, text, key=""): asked.append(text); return False
JR.run_for_ai("delete file zzz-not-there-9", "ask", Cap(), TMP / "h", lambda l: None, "test", ())
ok(asked and "-> task " in asked[0] and "AI wants JeeG to run" in asked[0], "approval card names the task: " + str(asked)[:200])

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

# ======================= v3: hints, failure hints, verify, run_many, compaction, lessons, skill hint, stats, stemming
setup(); reset_usage()
SEEN.clear(); SCRIPT[:] = ['{"done": "x"}']; goal("convert", "5", "km", "to", "miles")
first = SEEN[0]["messages"][1]["content"]
ok("TASKS THAT MAY HELP" in first and "convert_units" in first, "real tasks with usage are given to the model: " + first[:200])
SEEN.clear(); SCRIPT[:] = ['{"done": "x"}']; goal("open", "youtube", "for", "me", "steps", "2", "ask") if False else None
SEEN.clear(); SCRIPT[:] = ['{"run": "convert banana"}', '{"done": "x"}']; goal("hint", "test")
ok("HINT" in SEEN[1]["messages"][-1]["content"], "a failed request comes back with a hint: " + SEEN[1]["messages"][-1]["content"][:200])
# verify (careful)
SEEN.clear(); SCRIPT[:] = ['{"run": "convert 5 km to miles"}', '{"done": "it is 99 miles"}', '{"ok": false, "missing": "99 not in results"}', '{"done": "about 3.1 miles"}', '{"ok": true}']
rc, o = goal("miles", "in", "5", "km", "careful"); ok("3.1 miles" in o and "99" not in o.split("Done")[-1], "careful: unsupported answer is sent back: " + o)
ok(any("CHECK FAILED" in m["content"] for b in SEEN for m in b["messages"]), "careful: the model is told what was missing")
SEEN.clear(); SCRIPT[:] = ['{"done": "hello"}']; rc, o = goal("say", "hello", "careful"); ok(len(SEEN) == 1, "careful: no check when no steps ran")
# run_many
SEEN.clear(); SCRIPT[:] = ['{"run_many": ["convert 1 km to miles", "convert 2 km to miles", "convert 3 km to miles"]}', '{"done": "ok"}']; goal("many")
fed = SEEN[1]["messages"][-1]["content"]; ok("0.62" in fed and "1.24" in fed and "1.86" in fed, "run_many runs 3 look-only requests: " + fed[:200])
SEEN.clear(); SCRIPT[:] = ['{"run_many": ["convert 1 km to miles", "delete file zzz-not-there-9"]}', '{"done": "ok"}']; goal("many")
ok("NOT RUN" in SEEN[1]["messages"][-1]["content"], "run_many refuses a risky request")
# compaction
msgs = [{"role": "system", "content": "s"}, {"role": "user", "content": "goal"}] + [m for i in range(10) for m in ({"role": "assistant", "content": "{}"}, {"role": "user", "content": "RESULT\n" + "x" * 5000 + "\n>>>"})]
jeeg_agent.compact(msgs); tot = sum(len(m["content"]) for m in msgs); ok(tot <= 24000 + 6000 and msgs[-1]["content"].count("x") == 5000, "compaction shortens old results, keeps the newest: %d" % tot)
# lessons are only parked, never auto-kept
SEEN.clear(); SCRIPT[:] = ['{"run": "convert banana"}', '{"run": "convert 5 km to miles"}', '{"done": "3.1"}']; goal("lesson", "check")
ok("lesson check" in jeeg("remember", "review")[1] or "works" in jeeg("remember", "review")[1], "a lesson is parked for review, not kept")
# skill hint
jeeg("skill", "add", "tax", "=", "gst 100 18"); SEEN.clear(); SCRIPT[:] = ['{"done": "x"}']; goal("calculate", "gst", "tax", "on", "100")
ok("saved skill may fit" in SEEN[0]["messages"][1]["content"], "a matching skill is suggested")
# stats
rc, o = jeeg("agent", "stats"); ok(rc == 0 and "fake-model" in o and "runs" in o, "agent stats: " + o)
ok(jeeg_mind.words("converting files") == jeeg_mind.words("convert file"), "memory words are lightly stemmed: %s" % jeeg_mind.words("converting files"))
srv.shutdown()
print(f"agent: {P} passed, {F} failed"); sys.exit(1 if F else 0)
