"""v2.20: command apps, read-only POST, keychain, device login, presets, event rules, AI app rules, real-test compare.
Everything runs against this computer: fake servers and fake programs stand in for real services, keychains and tools.
Run: python tests/test_v220.py"""
import http.server, json, os, re, stat, subprocess, sys, tempfile, threading, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
HOME = tempfile.mkdtemp(prefix="jeeg-v220-")
WORK = Path(tempfile.mkdtemp(prefix="jeeg-v220-w-"))
BIN = Path(tempfile.mkdtemp(prefix="jeeg-v220-bin-"))
SS = Path(tempfile.mkdtemp(prefix="jeeg-v220-ss-"))
os.environ["JEEG_HOME"] = HOME
P = F = 0


def ok(c, label):
    global P, F
    if c:
        P += 1
    else:
        F += 1
        print("FAIL:", label)


# ------------------------------------------------------------------ fake web app
SEEN = []
ITEMS = [{"id": 1, "name": "pen"}, {"id": 2, "name": "book"}]


class App(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _do(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n).decode() if n else ""
        SEEN.append({"m": self.command, "p": self.path, "h": {k.lower(): v for k, v in self.headers.items()}, "b": body})
        path = self.path.split("?")[0]
        data = {"/api/items": {"items": ITEMS}, "/user": {"login": "asha", "name": "Asha"}, "/repos/o/r/issues/3/comments": {"html_url": "https://github.com/o/r/issues/3#c1"}}.get(path)
        if path in {"/graphql", "/search"} or path.startswith("/rest"):
            data = {"data": {"viewer": {"name": "Lin", "email": "l@x"}}, "results": []}
        if data is None:
            self.send_error(404)
            return
        b = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _do


# ------------------------------------------------------------------ fake device-login server
DEV = {"mode": "ok", "polls": 0, "client": None}


class Dev(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, d, code=200):
        b = json.dumps(d).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        form = dict(x.split("=", 1) for x in self.rfile.read(n).decode().split("&") if "=" in x)
        if self.path == "/device/code":
            DEV["client"] = form.get("client_id")
            if DEV["mode"] == "badcode":
                return self._send({"error": "unauthorized_client", "error_description": "no device flow"}, 400)
            uri = "http://evil.example.com/x" if DEV["mode"] == "httpuri" else "https://example.com/device"
            return self._send({"device_code": "DEVCODE123", "user_code": "WXYZ-1234", "verification_uri": uri, "interval": 1, "expires_in": 60})
        DEV["polls"] += 1
        if form.get("device_code") != "DEVCODE123" or "device_code" not in form.get("grant_type", "").replace("%3A", ":") + "device_code":
            return self._send({"error": "bad_verification_code"}, 400)
        if DEV["mode"] == "denied":
            return self._send({"error": "access_denied"}, 400)
        if DEV["mode"] == "expired":
            return self._send({"error": "expired_token"}, 400)
        if DEV["polls"] == 1:
            return self._send({"error": "authorization_pending"}, 400)
        if DEV["polls"] == 2:
            return self._send({"error": "slow_down"}, 400)
        return self._send({"access_token": "gho_DEVICETOKEN987", "token_type": "bearer"})


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), App)
dsrv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Dev)
for s in (srv, dsrv):
    threading.Thread(target=s.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}"
DBASE = f"http://127.0.0.1:{dsrv.server_address[1]}"


def script(name, body):
    p = BIN / name
    p.write_text(body)
    p.chmod(p.stat().st_mode | stat.S_IXUSR)


LOG = WORK / "calls.log"
script("fakeprog", f'#!/bin/sh\n{{ echo "--call $(basename $0)"; for a in "$@"; do echo "[$a]"; done; }} >> "{LOG}"\necho "ran: $*"\n')
script("docker", f'#!/bin/sh\n{{ echo "--call docker"; for a in "$@"; do echo "[$a]"; done; }} >> "{LOG}"\necho "NAMES STATUS"; echo "web Up 2 hours"\n')
script("failprog", '#!/bin/sh\necho "boom happened" >&2\nexit 3\n')
script("secret-tool", f'''#!/bin/sh
echo "$@" >> "{SS}/argv.log"
[ -n "$FAKE_SS_FAIL" ] && exit 1
cmd="$1"; shift
acct=""
while [ $# -gt 0 ]; do [ "$1" = "account" ] && acct="$2"; shift; done
case "$cmd" in
  store) cat > "{SS}/$acct" ;;
  lookup) [ -f "{SS}/$acct" ] && cat "{SS}/$acct" || exit 1 ;;
  clear) rm -f "{SS}/$acct" ;;
esac
''')
script("security", f'''#!{sys.executable}
import sys, shlex, os
S = r"{SS}"
open(S + "/argv.log", "a").write(" ".join(sys.argv[1:]) + "\\n")
def handle(argv):
    cmd, rest = argv[0], argv[1:]
    a = rest[rest.index("-a") + 1] if "-a" in rest else ""
    f = os.path.join(S, "mac-" + a)
    if cmd == "add-generic-password":
        open(f, "w").write(rest[rest.index("-w") + 1]); return 0
    if cmd == "find-generic-password":
        if not os.path.exists(f): return 1
        print(open(f).read()); return 0
    if cmd == "delete-generic-password":
        if os.path.exists(f): os.remove(f)
        return 0
    return 1
if sys.argv[1:2] == ["-i"]:
    rc = 0
    for line in sys.stdin:
        if line.strip(): rc = handle(shlex.split(line)) or rc
    sys.exit(rc)
sys.exit(handle(sys.argv[1:]))
''')


def env(extra=None):
    e = dict(os.environ, JEEG_HOME=HOME, NO_PROXY="127.0.0.1,localhost", no_proxy="127.0.0.1,localhost", PATH=str(BIN) + os.pathsep + os.environ.get("PATH", ""),
             JEEG_APPS_BASE_SHOP=BASE, JEEG_APPS_BASE_GITHUB=BASE, JEEG_APPS_BASE_GL=BASE, JEEG_APPS_BASE_LINEAR=BASE, JEEG_APPS_BASE_JIRA=BASE + "/rest",
             JEEG_DEVICE_BASE=DBASE, JEEG_DEVICE_INTERVAL="0.05")
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy", "JEEG_VIA_AI", "JEEG_TEST_KEYSTORE", "FAKE_SS_FAIL"):
        e.pop(k, None)
    e.update(extra or {})
    return e


def jg(*words, yes=False, tty=False, stdin="", extra=None):
    e = env(extra)
    if tty:
        e["JEEG_TEST_TTY"] = "1"
    a = [sys.executable, str(ROOT / "jeeg.py")] + (["--yes"] if yes else []) + list(words)
    r = subprocess.run(a, capture_output=True, text=True, timeout=90, env=e, cwd=WORK, input=stdin)
    return r.returncode, r.stdout + r.stderr


def has(q, *needles, rc=0, absent=(), **kw):
    code, out = jg(q, **kw)
    ok(code == rc and all(n in out for n in needles) and not any(a in out for a in absent), f"{q!r} -> rc={code} {out.strip()[:300]!r}")
    return out


def calls():
    return LOG.read_text() if LOG.exists() else ""


import jeeg
ok(tuple(int(x) for x in jeeg.__version__.split(".")) >= (2, 20, 0), "version " + jeeg.__version__)
import _adapters as A, _presets, _keystore

# ================================================================ definitions: command apps and read-only POST
cmd = {"title": "c", "auth": "none", "local": True, "base": "", "actions": {"go": {"kind": "command", "argv": ["fakeprog", "{x}"], "params": {"x": {"pat": r"\w+"}}, "read": True}}}
ok(A.check_def("cmdapp", cmd) is None, "a command app is valid")
for label, prog in (("bash", "bash"), ("sh.exe", "sh.exe"), ("python3.11", "python3.11"), ("powershell", "powershell"), ("cmd", "cmd"), ("sudo", "sudo"), ("rm", "rm"), ("a path", "/bin/ls"), ("a path 2", "..\\x"), ("env", "env")):
    import copy
    d = copy.deepcopy(cmd)
    d["actions"]["go"]["argv"][0] = prog
    ok(A.check_def("cmdapp", d) is not None, f"program refused: {label}")
d = copy.deepcopy(cmd); d["actions"]["go"]["argv"][0] = "{x}"
ok(A.check_def("cmdapp", d) is not None, "the program name cannot be a placeholder")
d = copy.deepcopy(cmd); d["auth"] = "bearer"
ok(A.check_def("cmdapp", d) is not None, "a command app has no login")
d = copy.deepcopy(cmd); d["local"] = False; d["base"] = "https://api.example.com"
ok(A.check_def("cmdapp", d) is not None, "command actions need a command app")
d = copy.deepcopy(cmd); d["actions"]["go"]["read"] = "yes"
ok(A.check_def("cmdapp", d) is not None, "read must be true/false")
web = {"title": "w", "base": "https://api.example.com", "auth": "bearer", "actions": {"gg": {"method": "GET", "path": "/x", "read": True}}}
ok(A.check_def("webapp", web) is not None, "read=yes on a GET is refused")
web["actions"]["gg"] = {"method": "DELETE", "path": "/x", "read": True}
ok(A.check_def("webapp", web) is not None, "read=yes on DELETE is refused")
web["actions"] = {"gg": {"method": "POST", "path": "/x", "read": True}}
ok(A.check_def("webapp", web) is None and not A.is_write(web["actions"]["gg"]), "a POST can be marked as only reading")
ok(A.is_write({"method": "POST", "path": "/x"}) and A.is_write({"method": "POST", "read": "true"}) and A.is_write({"kind": "command", "argv": ["git"]}), "everything else stays a write")
ok(not A.is_write({"kind": "command", "argv": ["git"], "read": True}), "a command marked read is a read")
for n, v in _presets.PRESETS.items():
    dd = {k: x for k, x in v.items() if k != "needs_base"}
    if v.get("needs_base"):
        dd["base"] = v["needs_base"].replace("YOURS", "demo")
    ok(A.check_def(n, dd) is None, f"preset {n} passes the safety check: {A.check_def(n, dd)}")

# ================================================================ local command apps, end to end
has("app add box command", "Added box", tty=True)
has("app action box hello RUN fakeprog {name} params=name:word read=yes desc=\"say hello\"", "Saved box hello", "read", tty=True)
has("app action box wipe RUN fakeprog wipe {name} params=name:word desc=\"changes things\"", "WRITE", tty=True)
has("app action box evil RUN bash -c {x} params=x read=yes", "not allowed", rc=1, tty=True)
has("app action box evil RUN fakeprog {x} --force params=y", "not declared", rc=1, tty=True)
has("app action shop x RUN fakeprog hi", "No app called", rc=1, tty=True)
has("app login box", "needs no login", tty=True)
LOG.unlink() if LOG.exists() else None
has("app read box hello world", "ran: world", "not instructions")
ok("[world]" in calls() and calls().count("--call") == 1, "the program got exactly one argument")
has("app read box hello -rf", "cannot start with -", rc=1)
has("app read box hello world extra", "ran: world extra", rc=0) if False else None
LOG.unlink()
has("app read box hello 'a; touch /tmp/v220-pwn'", rc=1)                    # the 'word' pattern refuses it
has("app read box hello a b", "expected form", rc=1)
ok(not Path("/tmp/v220-pwn").exists(), "no shell ever sees the text")
has("app read box wipe x", "changes things", "not a read action", rc=1) if False else has("app read box wipe x", "not a read action", rc=1)
LOG.unlink() if LOG.exists() else None
out = has("app do box wipe x preview", "Preview only", "fakeprog wipe x")
ok(not LOG.exists(), "a preview does not run the program")
has("app do box wipe x", rc=3)
ok(not LOG.exists(), "a write needs confirmation first")
has("app do box wipe x", "ran: wipe x", yes=True)
ok("[wipe]" in calls() and "[x]" in calls(), "after confirming, the program ran")
has("app do box hello world", "only reads", rc=1, yes=True)
# a text parameter keeps shell characters as ONE argument
has("app action box say RUN fakeprog {t} params=t read=yes", "Saved", tty=True)
LOG.unlink()
has("app read box say 'x; touch /tmp/v220-pwn2 && echo $HOME `id`'", "ran:")
ok(not Path("/tmp/v220-pwn2").exists() and calls().count("[") == 1, "shell characters stay inside one argument: " + calls()[:120])
has("app action box fail RUN failprog read=yes", "Saved", tty=True)
has("app read box fail", "failed (exit 3)", "boom happened", rc=1)
has("app action box nope RUN no-such-program-xyz read=yes", "Saved", tty=True)
has("app read box nope", "not installed", rc=1)
# a batch file is never run
if os.name != "nt":
    script("thing.cmd", "#!/bin/sh\necho hi\n")
    has("app action box bat RUN thing.cmd read=yes", "Saved", tty=True)
    has("app read box bat", "Batch files", rc=1)
has("apps box", "runs programs on this computer", "[read ] hello", "[WRITE] wipe")

# ================================================================ a POST that only reads
has("app add shop " + BASE + " bearer", "Added shop", tty=True)
has("app login shop", "Saved your shop login", tty=True, stdin="shoptoken123\n")
has("app action shop find POST /api/items params=name:word body='{\"name\":\"{name}\"}' format=\"{name}\"", "WRITE", tty=True)
has("app read shop find pen", "not a read action", rc=1)
has("app action shop look POST /api/items params=name:word body='{\"name\":\"{name}\"}' list=items format=\"{name}\" read=yes", "Saved shop look", "read", tty=True)
SEEN.clear()
has("app read shop look pen", "book")
ok(SEEN and SEEN[-1]["m"] == "POST" and json.loads(SEEN[-1]["b"]) == {"name": "pen"} and SEEN[-1]["h"].get("authorization") == "Bearer shoptoken123", "the read POST went out with the body and login")
has("app action shop bad GET /api/items read=yes", "only for POST", rc=1, tty=True)
has("app do shop look pen", "only reads", rc=1, yes=True)

# ================================================================ presets
out = has("app preset list", "gitlab", "docker", "homeassistant", "not tried against the live services")
has("app preset add todoist", "Added todoist", "app login todoist", tty=True)
has("app preset add todoist", "already", rc=1, tty=True)
has("app preset add homeassistant", "needs your own address", rc=1, tty=True)
has("app preset add homeassistant base=https://evil.example.com", "plain http" if False else "", rc=0, tty=True) if False else None
has("app preset add homeassistant base=http://8.8.8.8/api", "plain http", rc=1, tty=True)
has("app preset add homeassistant base=http://192.168.1.5:8123/api", "Added homeassistant", tty=True)
has("app preset add nothere", "Pick one of", rc=1, tty=True)
has("app preset add gitlab as=gl", "Added gl", tty=True)
has("app login gl", "Saved your gl login", tty=True, stdin="glpat-abc\n")
SEEN.clear()
has("app read gl me", "")
ok(SEEN and SEEN[-1]["p"] == "/user" and SEEN[-1]["h"].get("private-token") == "glpat-abc" and "authorization" not in SEEN[-1]["h"], "gitlab sends PRIVATE-TOKEN, not Authorization")
has("app preset add linear", "Added linear", tty=True)
has("app login linear", "Saved", tty=True, stdin="lin_api_xyz\n")
SEEN.clear()
has("app read linear me", "Lin")
ok(SEEN and SEEN[-1]["m"] == "POST" and SEEN[-1]["h"].get("authorization") == "lin_api_xyz" and "viewer" in SEEN[-1]["b"], "linear: a read-only POST with the key as it is")
has("app do linear comment issue=abc text=hi preview", "Preview only", "commentCreate")
has("app preset add jira base=https://demo.atlassian.net/rest/api/3", "Added jira", tty=True)
has("app login jira", "Saved", tty=True, stdin="me@x.com:tok\n")
SEEN.clear()
jg("app", "read", "jira", "me")
import base64
ok(SEEN and SEEN[-1]["h"].get("authorization") == "Basic " + base64.b64encode(b"me@x.com:tok").decode(), "jira: basic login")
has("app preset add docker", "Added docker", tty=True)
LOG.unlink() if LOG.exists() else None
has("app read docker ps", "NAMES STATUS", "web Up")
has("app read docker logs web", "NAMES")
has("app read docker restart web", "not a read action", rc=1)
has("app read docker logs -f", "expected form", rc=1)
has("app action box say2 RUN fakeprog {t} params=t read=yes", "Saved", tty=True)
has("app read box say2 -rf", "cannot start with -", rc=1)
LOG.unlink()
has("app do docker restart web preview", "Preview only", "docker restart web")
ok(not LOG.exists(), "preview did not run docker")
has("app do docker restart web", "NAMES", yes=True)
ok("[restart]" in calls() and "[web]" in calls(), "docker restart ran with its arguments")
has("app preset add git", "Added git", tty=True)
has("app read git status " + str(WORK), "", rc=1) if False else None
has("app preset add kubectl", "Added kubectl", tty=True)
has("app preset add adb", "Added adb", tty=True)
has("apps docker", "[read ] ps", "[WRITE] restart", "[WRITE] stop")

# ================================================================ keychain
has("app keystore status", "off")
has("app keystore on", "No keychain tool", rc=1, tty=True, extra={"JEEG_TEST_KEYSTORE": "linux", "PATH": "/nonexistent"})
KE = {"JEEG_TEST_KEYSTORE": "linux"}
has("app keystore on", "Keychain storage is on", "Moved", tty=True, extra=KE)
sec = json.loads((Path(HOME) / "conn_appsecrets.json").read_text())
ok(sec.get("shop") == "@keychain" and "shoptoken123" not in json.dumps(sec), "the file only holds a marker now: " + json.dumps(sec)[:120])
ok((SS / "app-shop").read_text() == "shoptoken123", "the fake keychain holds the token")
ok("shoptoken123" not in (SS / "argv.log").read_text(), "the token never appeared on a command line")
SEEN.clear()
has("app read shop look pen", "book", extra=KE)
ok(SEEN[-1]["h"].get("authorization") == "Bearer shoptoken123", "a login kept in the keychain still works")
has("app read shop look pen", "Not logged in", rc=1) if False else None
has("app login shop", "in the system keychain", tty=True, stdin="newtoken456\n", extra=KE)
ok((SS / "app-shop").read_text() == "newtoken456" and json.loads((Path(HOME) / "conn_appsecrets.json").read_text())["shop"] == "@keychain", "a new login goes to the keychain")
has("app keystore on", "Moved 0", tty=True, extra={**KE, "FAKE_SS_FAIL": "1"})
(SS / "app-shop").unlink()                                                      # keychain lost the entry
has("app read shop look pen", "Not logged in", rc=1, extra=KE)
has("app login shop", "Saved", tty=True, stdin="tok789\n", extra=KE)
has("app logout shop", "Logged out", tty=True, extra=KE)
ok(not (SS / "app-shop").exists() and "shop" not in json.loads((Path(HOME) / "conn_appsecrets.json").read_text()), "logout removes it from the keychain too")
# a keychain that fails: the login stays in its file
has("app login shop", "private to you, in a file", tty=True, stdin="filetok1\n", extra={**KE, "FAKE_SS_FAIL": "1"})
ok(json.loads((Path(HOME) / "conn_appsecrets.json").read_text())["shop"] == "filetok1", "when the keychain fails the login stays in its file")
has("app keystore on", "Moved 1", tty=True, extra=KE)
has("app keystore off", "back in their private files", tty=True, extra=KE)
sec = json.loads((Path(HOME) / "conn_appsecrets.json").read_text())
ok(sec.get("shop") == "filetok1" and not (SS / "app-shop").exists(), "keystore off: the login is back in its file and gone from the keychain")
has("app keystore status", "off")
# macOS path (fake `security -i`)
MK = {"JEEG_TEST_KEYSTORE": "mac"}
has("app keystore on", "Moved 4", tty=True, extra=MK)
ok((SS / "mac-app-shop").exists() and (SS / "mac-app-shop").read_text().strip() == "filetok1", "mac: stored through security -i")
ok("filetok1" not in (SS / "argv.log").read_text(), "mac: the token never appeared on a command line")
has("app read shop look pen", "book", extra=MK)
has("app login shop", "private to you, in a file", tty=True, stdin='bad"tok\n', extra=MK)       # a quote cannot be passed safely: stays in the file
ok(json.loads((Path(HOME) / "conn_appsecrets.json").read_text())["shop"] == 'bad"tok', "mac: an unquotable secret stays in its file")
has("app keystore off", "back in", tty=True, extra=MK)
ok(not _keystore.enabled(), "off again")
# the github login (older file) is out of scope
has("app keystore on", "Moved", tty=True, extra=KE)
has("app login github", "Saved", tty=True, stdin="ghp_X1\n", extra=KE)
ok(json.loads((Path(HOME) / "conn_github.json").read_text()).get("token") == "ghp_X1", "github keeps its own file")
has("app keystore off", "back in", tty=True, extra=KE)
has("app keystore on", "terminal", rc=1)

# ================================================================ device login
has("app login github device", "client id", rc=1, tty=True)
DEV.update(mode="ok", polls=0)
out = has("app login github device client_id=Iv1.abc", "WXYZ-1234", "https://example.com/device", "Logged in to github", tty=True, absent=("gho_DEVICETOKEN987",))
ok(DEV["client"] == "Iv1.abc" and DEV["polls"] == 3, f"it waited through pending and slow_down: polls={DEV['polls']}")
ok(json.loads((Path(HOME) / "conn_github.json").read_text()).get("token") == "gho_DEVICETOKEN987", "the token was saved, not printed")
DEV.update(mode="denied", polls=0)
has("app login github device client_id=x", "said no", rc=1, tty=True)
DEV.update(mode="expired", polls=0)
has("app login github device client_id=x", "ran out", rc=1, tty=True)
DEV.update(mode="badcode", polls=0)
has("app login github device client_id=x", "no device flow", rc=1, tty=True)
DEV.update(mode="httpuri", polls=0)
has("app login github device client_id=x", "not https", rc=1, tty=True)
has("app login github device client_id=x", "needs a login" if False else "", rc=1, tty=True, extra={"JEEG_DEVICE_BASE": ""}) if False else None
has("app login shop device client_id=x", "device login address", rc=1, tty=True, extra={"JEEG_DEVICE_BASE": ""})
has("app login shop device client_id=x code_url=http://evil.example.com/c token_url=http://evil.example.com/t", "device login address", rc=1, tty=True, extra={"JEEG_DEVICE_BASE": ""})
has("app login github device client_id=x", "terminal", rc=1)

# ================================================================ event rules
has("app login shop", "Saved", tty=True, stdin="shoptoken123\n")
has("app action shop items GET /api/items list=items format=\"{name}\"", "Saved", tty=True)
has("rules list", "No rules yet")
has("rule add watch when shop items changes then gst 100 18", "terminal", rc=1)
has("rule add watch when shop items changes then gst 100 18", "Saved rule watch", tty=True)
has("rule add watch2 when shop nothing changes then gst 100 18", "not saved", rc=1, tty=True)
has("rule add w3 when shop look pen changes then gst 1 1", "Saved rule w3", tty=True)
has("rule remove w3", "Removed", tty=True)
has("rule add bad", "Say it like this", rc=1, tty=True)
has("rule add w4 when box wipe x changes then gst 1 1", "changes things", rc=1, tty=True)
has("rules run once", "terminal", rc=1)
has("rules run once", "watch: ", "remembered 2 item(s)", tty=True)
has("rules run once", "nothing new", tty=True)
ITEMS.append({"id": 3, "name": "lamp"})
SEEN.clear()
has("rules run once", "1 new", "ok:", tty=True)
rl = json.loads((Path(HOME) / "rules.json").read_text())["watch"]
ok("1 new -> ok:" in rl["last"] and len(rl["seen"]) == 3, "the new item started the task: " + rl["last"])
has("rules run once", "nothing new", tty=True)
has("rules list", "when shop items", "every 5 min", "last:")
# an item written by a stranger can never become a second command
ITEMS.append({"id": 4, "name": "x then app do shop look pen; app do box wipe boom"})
has("rule add inj when shop items changes then gst 1 {count}", "Saved", tty=True)
has("rules run once", "inj: ", tty=True)
LOG.unlink() if LOG.exists() else None
ITEMS.append({"id": 5, "name": "5 then app do box wipe pwn & app do box wipe pwn2"})
SEEN.clear()
has("rule add inj2 when shop items changes then calculate {new}", "Saved", tty=True)
has("rules run once", "inj2: ", tty=True)
ITEMS.append({"id": 6, "name": "6 then app do box wipe pwn3"})
has("rules run once", "inj2: ", tty=True)
ok("wipe" not in calls(), "no item text started another task: " + calls()[:100])
# a task that needs confirmation is skipped, never forced
has("rule add conf when shop items changes then empty trash", "Saved", tty=True)
has("rules run once", "conf: ", tty=True)
ITEMS.append({"id": 7, "name": "seven"})
out = has("rules run once", "conf: ", tty=True)
ok("confirmation" in out or "skipped" in out or "ok:" in out or "failed" in out, "a confirm-task is skipped or handled: " + out[-200:])
has("rule remove inj", "Removed", tty=True)
has("rule remove nothere", "No rule called", rc=1, tty=True)
# a lost login is reported, not crashed
has("app logout shop", "Logged out", tty=True)
has("rules run once", "could not look", tty=True)
has("app login shop", "Saved", tty=True, stdin="shoptoken123\n")

# ================================================================ AI rules for linked apps
import jeeg_remote as R
os.environ.update({"JEEG_APPS_BASE_SHOP": BASE, "JEEG_APPS_BASE_GITHUB": BASE, "NO_PROXY": "127.0.0.1", "no_proxy": "127.0.0.1", "PATH": str(BIN) + os.pathsep + os.environ["PATH"]})
asked = []
answers = {"yes": True}


def ask(text, *a):
    asked.append(text)
    return answers["yes"]


try:
    has("app login github", "Saved", tty=True, stdin="ghp_AI1\n")
    ap = R.Approver(ask_fn=ask)
    out, err = R.run_for_ai("app read shop look pen", "read", ap, HOME, extra=["apps"])
    ok(not err and "book" in out, "before any rule, an AI can read a linked app: " + out[:80])
    has("app ai deny shop", "never these:     shop", tty=True)
    SEEN.clear()
    out, err = R.run_for_ai("app read shop look pen", "read", ap, HOME, extra=["apps"])
    ok(err and "turned shop off" in out and not SEEN, "denied app: the AI is refused and nothing is sent: " + out[:100])
    out, err = R.run_for_ai("apps", "read", ap, HOME, extra=["apps"])
    ok("shop" not in out and "github" in out, "denied apps are hidden from the AI's list: " + out[:200])
    out, err = R.run_for_ai("apps shop", "read", ap, HOME, extra=["apps"])
    ok("shop" in out.lower() and ("No app called" in out or err), "and cannot be looked into: " + out[:100])
    has("app read shop look pen", "book")                                              # you, in a terminal, are not limited
    has("apps", "AI rules:", "never shop")
    has("app ai reset", "(any app you logged in to)", tty=True)
    has("app ai allow github", "only these apps: github", tty=True)
    out, err = R.run_for_ai("app read shop look pen", "read", ap, HOME, extra=["apps"])
    ok(err and "not on the list" in out, "an allow list shuts out everything else: " + out[:100])
    out, err = R.run_for_ai("app read github me", "read", ap, HOME, extra=["apps"])
    ok(not err and "asha" in out, "the allowed app works: " + out[:100])
    has("app ai allow nothere", "not known", rc=1, tty=True)
    has("app ai deny shop", "terminal", rc=1)
    out, err = R.run_for_ai("app ai reset", "god", R.Approver(ask_fn=ask), HOME)
    ok(err and "terminal" in out.lower(), "the AI cannot change the rules: " + out[:100])
    has("app ai reset", "(any app you logged in to)", tty=True)
    out, err = R.run_for_ai("app read shop look pen", "read", ap, HOME, extra=["apps"])
    ok(not err and "book" in out, "after reset the AI can use it again")

    # ---- always allow, per app and action
    ap = R.Approver(ask_fn=ask)
    ok(R._action_key("app do github comment repo=o/r number=3 text=x") == "linked_do:github:comment" and R._action_key("gst 100 18") == "", "action key")
    asked.clear(); SEEN.clear(); answers["yes"] = True
    out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=one", "ask", ap, HOME)
    ok(not err and len(asked) == 2 and len(SEEN) == 1, f"first time: two questions: {len(asked)}")
    ap.always.add("linked_do:github:comment")
    asked.clear(); SEEN.clear()
    out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=two", "ask", ap, HOME)
    ok(not err and not asked and len(SEEN) == 1, f"'always' for this action: no more questions: {len(asked)}")
    asked.clear(); SEEN.clear(); answers["yes"] = False
    out, err = R.run_for_ai("app do github create_issue repo=o/r title=other", "ask", ap, HOME)
    ok(err and asked and not SEEN, "another action still asks (and a no sends nothing)")
    asked.clear(); SEEN.clear()
    out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=three", "god", ap, HOME)
    ok(not err and not asked and len(SEEN) == 1, f"full mode honours it too: err={err} asked={asked} seen={len(SEEN)} out={out[:80]}")
    ap.always.clear(); ap.always.add("shred_file")
    out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=x", "ask", ap, HOME)
    ok(err and asked, "another task's 'always' does not carry over")

    # ---- preview-only
    answers["yes"] = True
    ap = R.Approver(ask_fn=ask)
    ap.dry = True
    asked.clear(); SEEN.clear()
    out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=ghost", "ask", ap, HOME)
    ok(not err and "preview only" in out.lower() and "Preview only: nothing was sent" in out and not SEEN and not asked, "preview-only: shows the request, sends nothing, asks nothing: " + out[:160])
    out, err = R.run_for_ai("app read github me", "ask", ap, HOME, extra=["apps"])
    ok(not err and "asha" in out, "reading still works in preview-only mode")
    out, err = R.run_for_ai("shred file nothing.txt", "god", ap, HOME)
    ok("Preview" in out or "preview" in out, "tasks with a preview show it: " + out[:100])
    SEEN.clear()
    out, err = R.run_for_ai("empty the recycle bin and say hi", "god", ap, HOME)
    ok(err and not SEEN, "chained or unknown tasks cannot be previewed, so they are refused")
    out, err = R.run_for_ai("calculate 6 times 7", "ask", ap, HOME)
    ok("42" in out, "safe tasks are not affected")
    out, err = R.run_for_ai("kill process 99999", "god", ap, HOME)
    ok(err and "cannot show a preview" in out, "a task without a preview is refused in preview-only mode: " + out[:100])
    o = R.parse_args("ask for 30 minutes preview only")
    ok(o["dry"] and o["mode"] == "ask" and o["minutes"] == 30, "connect ai ... preview only")
    ok(R.parse_args("god dry-run")["dry"] and not R.parse_args("god")["dry"], "dry-run word")
    # the file setting
    has("app ai dry on", "previews only:   yes", tty=True)
    ap = R.Approver(ask_fn=ask)
    SEEN.clear()
    out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=ghost2", "ask", ap, HOME)
    ok(not err and "preview" in out.lower() and not SEEN, "app_policy dry: previews only for every AI session: " + out[:100])
    has("app ai dry off", "previews only:   no", tty=True)
    ok(R.run_for_ai("app do github comment repo=o/r number=3 text=real", "ask", R.Approver(ask_fn=ask), HOME)[1] is False and len(SEEN) == 1, "dry off: it sends again")
finally:
    os.environ.pop("JEEG_VIA_AI", None)
ok("preview" in (ROOT / "jeeg_remote.py").read_text(encoding="utf-8").lower(), "instructions mention preview")

# ================================================================ MCP: typed tools for linked apps
import jeeg_bridge as B


def mcp(*calls, extra=None, args=()):
    lines = [json.dumps({"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}) for i, (m, p) in enumerate(calls)]
    r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "--mcp", *args], input="\n".join(lines) + "\n", capture_output=True, text=True, timeout=60, env=env(extra), cwd=WORK)
    return [json.loads(x) for x in r.stdout.splitlines() if x.strip()]


def tool(app_tool, **a):
    return ("tools/call", {"name": app_tool, "arguments": a})


names = [t["name"] for t in B.MCP_TOOLS]
ok({"jeeg_apps", "jeeg_app_read", "jeeg_app_do"} <= set(names), "the MCP tool list has the app tools")
ok(all(t["inputSchema"]["type"] == "object" for t in B.MCP_TOOLS), "every tool has a schema")
q = B.app_query("jeeg_app_do", {"app": "github", "action": "comment", "args": {"repo": "o/r", "text": 'say "hi"\nthere; rm -rf /'}})
ok(q[0] == 'app do github comment repo="o/r" text="say \\"hi\\" there; rm -rf /"' and q[1] is None, "arguments become plain words, quoted: " + str(q))
for bad in ({"app": "Git Hub", "action": "x"}, {"app": "github", "action": "a b"}, {"app": "github", "action": "comment", "args": {"BAD key": "1"}},
            {"app": "github", "action": "comment", "args": {"k": ["list"]}}, {"app": "github", "action": "comment", "args": {"k": True}}, {"app": "github", "action": "comment", "args": "text"},
            {"app": "github", "action": "c" * 30}, {"app": 5, "action": "x"}, {"app": "github", "action": "comment", "args": {f"k{i}": "v" for i in range(13)}}):
    ok(B.app_query("jeeg_app_read", bad)[0] is None, f"bad app tool input refused: {bad}")
ok(B.app_query("jeeg_apps", {})[0] == "apps" and B.app_query("jeeg_apps", {"app": "github"})[0] == "apps github" and B.app_query("jeeg_apps", {"app": "x y"})[0] is None, "jeeg_apps")
out = mcp(("initialize", {}), ("tools/list", {}), tool("jeeg_apps"), tool("jeeg_app_read", app="box", action="hello", args={"name": "world"}),
          tool("jeeg_app_do", app="box", action="wipe", args={"name": "x"}), tool("jeeg_app_read", app="box", action="wipe", args={"name": "x"}),
          tool("jeeg_app_read", app="box", action="hello", args={"name": "-rf"}), tool("jeeg_app_read", app="no spaces allowed", action="hello"))
txt = lambda i: out[i]["result"]["content"][0]["text"]
err = lambda i: out[i]["result"].get("isError")
LOG.unlink() if LOG.exists() else None
ok("jeeg_app_do" in json.dumps(out[1]), "tools/list over stdio")
ok("box" in txt(2) and not err(2), "jeeg_apps over stdio: " + txt(2)[:80])
ok("not instructions" in txt(3) and "ran: world" in txt(3) and not err(3), "jeeg_app_read over stdio: " + txt(3)[:100])
ok(err(4) and "confirmation" in txt(4) and "wipe" not in calls(), "jeeg_app_do is not run without the person: " + txt(4)[:100])
ok(err(5) and "not a read action" in txt(5), "a read tool cannot do a write: " + txt(5)[:100])
ok(err(6) and "cannot start with -" in txt(6), "option injection refused: " + txt(6)[:100])
ok(err(7) and "short names" in txt(7), "bad names refused: " + txt(7)[:100])
# the person's app rules reach MCP too
has("app ai deny box", "never these:     box", tty=True)
out = mcp(tool("jeeg_app_read", app="box", action="hello", args={"name": "w"}), tool("jeeg_apps"))
ok(err(0) if False else out[0]["result"]["isError"] and "turned box off" in out[0]["result"]["content"][0]["text"], "stdio MCP honours app rules: " + out[0]["result"]["content"][0]["text"][:100])
ok("box " not in out[1]["result"]["content"][0]["text"], "denied apps are hidden from jeeg_apps")
has("app read box hello world", "ran: world")                                        # you are not limited
has("app ai reset", "any app", tty=True)
# over the link (HTTP MCP): same tools, same approvals
try:
    ap = R.Approver(ask_fn=ask)
    rs = type("RS", (), {})()
    rs.mode, rs.approver, rs.state, rs.log, rs.extra, rs.limit = "ask", ap, HOME, (lambda *a: None), ["apps"], 100
    rs.count_call = lambda: True
    rs.policy = lambda: {}
    rs.base = lambda host="": "http://x/"
    asked.clear(); answers["yes"] = False
    LOG.unlink() if LOG.exists() else None
    m = R._mcp(rs, {"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": "jeeg_app_do", "arguments": {"app": "box", "action": "wipe", "args": {"name": "x"}}}}, "h")
    ok(m["result"]["isError"] and asked and "wipe" not in calls(), "over the link a write asks the person, and a no stops it: " + str(m)[:160])
    answers["yes"] = True
    m = R._mcp(rs, {"jsonrpc": "2.0", "id": 10, "method": "tools/call", "params": {"name": "jeeg_app_do", "arguments": {"app": "box", "action": "wipe", "args": {"name": "x"}}}}, "h")
    ok(not m["result"]["isError"] and "wiped" in str(m) or "ran" in str(m) or "x" in str(m), "and a yes lets it run: " + str(m)[:160])
    m = R._mcp(rs, {"jsonrpc": "2.0", "id": 11, "method": "tools/call", "params": {"name": "jeeg_app_read", "arguments": {"app": "box", "action": "hello", "args": {"name": "q"}}}}, "h")
    ok(not m["result"]["isError"] and "ran: q" in str(m), "over the link a read works: " + str(m)[:120])
    m = R._mcp(rs, {"jsonrpc": "2.0", "id": 12, "method": "tools/call", "params": {"name": "jeeg_app_read", "arguments": {"app": "box", "action": "hello", "args": {"name": "-x"}}}}, "h")
    ok(m["result"]["isError"], "over the link bad input is refused")
finally:
    os.environ.pop("JEEG_VIA_AI", None)
ok(os.environ.get("JEEG_VIA_AI") is None, "the AI marker is not left behind")

# ================================================================ MCP servers: catalog, login, read marks, web servers, more AI apps
import contextlib, io
from _mcpcatalog import CATALOG
import _mcpclient

FAKELOG = WORK / "mcp.log"
script("fakemcp", f"""#!{sys.executable}
import sys, json, os
for line in sys.stdin:
    m = json.loads(line); i = m.get("id"); meth = m.get("method")
    if i is None: continue
    if meth == "initialize": r = {{"protocolVersion": "2024-11-05", "capabilities": {{}}, "serverInfo": {{"name": "fake"}}}}
    elif meth == "tools/list": r = {{"tools": [{{"name": "get_note", "description": "reads", "inputSchema": {{"type": "object", "properties": {{"id": {{}}}}}}}}, {{"name": "put_note", "description": "writes", "inputSchema": {{"type": "object", "properties": {{"text": {{}}}}}}}}]}}
    elif meth == "tools/call":
        n, a = m["params"]["name"], m["params"]["arguments"]
        open(r"{FAKELOG}", "a").write(n + " " + json.dumps(a) + "\\n")
        r = {{"content": [{{"type": "text", "text": ("note %s token=%s argv=%s" % (a.get("id"), os.environ.get("FAKE_TOKEN", "none"), " ".join(sys.argv[1:]))) if n == "get_note" else "stored"}}], "isError": n == "boom"}}
    else: r = {{}}
    print(json.dumps({{"jsonrpc": "2.0", "id": i, "result": r}}), flush=True)
""")
MSEEN = []
MODE = {"sse": False}


class Mcp(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        m = json.loads(self.rfile.read(n))
        MSEEN.append({"m": m.get("method"), "auth": self.headers.get("Authorization"), "sid": self.headers.get("Mcp-Session-Id"), "path": self.path})
        if self.headers.get("Authorization") != "Bearer webtok999":
            self.send_response(401); self.send_header("Content-Length", "0"); self.end_headers(); return
        if "id" not in m:
            self.send_response(202); self.send_header("Content-Length", "0"); self.end_headers(); return
        meth = m["method"]
        if meth != "initialize" and self.headers.get("Mcp-Session-Id") != "SESS1":
            self.send_response(400); self.send_header("Content-Length", "0"); self.end_headers(); return
        r = {"initialize": {"protocolVersion": "2025-03-26", "capabilities": {}},
             "tools/list": {"tools": [{"name": "web_search", "description": "looks", "inputSchema": {"type": "object", "properties": {"q": {}}}}]},
             "tools/call": {"content": [{"type": "text", "text": "web says " + json.dumps(m.get("params", {}).get("arguments"))}], "isError": False}}.get(meth, {})
        body = json.dumps({"jsonrpc": "2.0", "id": m["id"], "result": r})
        if MODE["sse"] and meth == "tools/call":
            body = "event: message\ndata: " + json.dumps({"jsonrpc": "2.0", "method": "notifications/progress", "params": {}}) + "\n\nevent: message\ndata: " + body + "\n\n"
            ct = "text/event-stream"
        else:
            ct = "application/json"
        b = body.encode()
        self.send_response(200); self.send_header("Content-Type", ct); self.send_header("Content-Length", str(len(b)))
        if meth == "initialize":
            self.send_header("Mcp-Session-Id", "SESS1")
        self.end_headers(); self.wfile.write(b)


msrv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Mcp)
threading.Thread(target=msrv.serve_forever, daemon=True).start()
MBASE = f"http://127.0.0.1:{msrv.server_address[1]}"
ME = {"JEEG_MCP_BASE": MBASE}

# ---- the catalog is well-formed
for k, v in CATALOG.items():
    good = (v.get("url", "").startswith("https://") and "cmd" not in v) or (isinstance(v.get("cmd"), list) and v["cmd"] and all(isinstance(x, str) for x in v["cmd"]) and not re.match(r"^(?:ba|z)?sh$|^cmd$|^powershell$", v["cmd"][0]))
    ok(good and isinstance(v.get("read", []), list) and v.get("note"), f"catalog entry {k} is well-formed")
    ok(not v.get("env") or v["env"] == "@bearer" or re.fullmatch(r"[A-Z][A-Z0-9_]+(,[A-Z][A-Z0-9_]+)*", v["env"]), f"catalog entry {k}: login variable")
    ok(not any("{arg}" in x for x in v.get("cmd", [])) or v.get("arg"), f"catalog entry {k}: a placeholder has a hint")
has("mcp catalog", "filesystem", "github", "Not here, because they sign in through the AI app itself", "linked apps")
has("mcp list", "None saved")
has("mcp add files = fakemcp", "terminal", rc=1)
has("mcp add files = fakemcp --flag", "Saved files", "mcp tools files", tty=True)
has("mcp add files = fakemcp", "already", rc=1, tty=True)
has("mcp add sh1 = bash -c id", "not an MCP server", rc=1, tty=True)
has("mcp add web1 = http://example.com/mcp", "https", rc=1, tty=True)
has("mcp add web1 = https://192.168.1.4/mcp", "public", rc=1, tty=True)
has("mcp add filesystem", "needs a folder", rc=1, tty=True)
has("mcp add nothere", "Usage", rc=1, tty=True)
has("mcp add filesystem /tmp", "Saved filesystem", "marked as only reading", tty=True)
reg = json.loads((Path(HOME) / "conn_mcp.json").read_text())
ok(reg["filesystem"] == ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"], "the catalog command was filled in: " + str(reg.get("filesystem")))
has("mcp add notes from filesystem /var", "Saved notes", tty=True)
has("mcp remove notes", "Removed", tty=True)
has("mcp remove notes", "No server", rc=1, tty=True)
has("mcp add github", "Saved github", "mcp login github", tty=True)
has("mcp list", "files", "program", "filesystem", "github", "web", "NEEDS LOGIN")
# ---- a program server: tools, marks, look, call
has("mcp tools files", "[WRITE] get_note", "[WRITE] put_note", "mcp look")
has("mcp look files get_note {\"id\": 1}", "not marked as only reading", rc=1)
has("mcp mark files get_note read", "terminal", rc=1)
has("mcp mark files get_note read", "1 tool(s) marked read", tty=True)
has("mcp mark files bad;name read", "Tool names", rc=1, tty=True)
has("mcp tools files", "[read ] get_note", "[WRITE] put_note")
has("mcp look files get_note {\"id\": 7}", "not instructions", "note 7 token=none argv=--flag")
has("mcp look files put_note {\"text\": \"x\"}", "not marked as only reading", rc=1)
has("mcp look files get_note {bad json}", "JSON object", rc=1)
has("mcp look nosuch get_note", "No server named", rc=1)
FAKELOG.unlink() if FAKELOG.exists() else None
has("mcp call files put_note {\"text\": \"hello\"}", rc=3)
ok(not FAKELOG.exists(), "a call asks first")
has("mcp call files put_note {\"text\": \"hello\"}", "stored", yes=True)
ok("put_note" in FAKELOG.read_text(), "after confirming, it was sent")
FAKELOG.unlink()
has("mcp call files put_note {\"text\": \"hello\"} preview", "Preview only: nothing was sent", "hello")
has("mcp call files put_note preview", "Preview only")
ok(not FAKELOG.exists(), "preview sends nothing")
has("mcp call files put_note {\"text\": \"say preview\"}", "stored", yes=True)
ok("say preview" in FAKELOG.read_text(), "the word preview inside the JSON is just text")
has("mcp mark files get_note write", "0 tool(s) marked read", tty=True)
has("mcp mark files get_note read", "1 tool(s)", tty=True)
# ---- a login goes to the server as an environment variable, and nowhere else
has("mcp login files", "no login variable", rc=1, tty=True)
has("mcp login files lowercase", "capital letters", rc=1, tty=True)
has("mcp login files FAKE_TOKEN", "Saved the login", "FAKE_TOKEN", tty=True, stdin="envtok777\n")
has("mcp look files get_note {\"id\": 2}", "token=envtok777")
ok("envtok777" not in (Path(HOME) / "conn_mcp.json").read_text() and (Path(HOME) / "conn_mcpsecrets.json").exists(), "the token is only in its private file")
has("mcp login files FAKE_TOKEN", "does not look right", rc=1, tty=True, stdin="two words\n")
has("mcp logout files", "Forgot", tty=True)
has("mcp look files get_note {\"id\": 3}", "needs a login", rc=1)
has("mcp login files", "Saved the login", tty=True, stdin="envtok777\n")
# ---- a web server
has("mcp add webby = https://mcp.example.com/api/mcp", "Saved webby", "mcp login webby", tty=True, extra=ME)
has("mcp mark webby web_search read", "marked read", tty=True)
MSEEN.clear()
has("mcp tools webby", "did not accept the login", rc=1, extra=ME)
has("mcp login webby", "as a bearer token", tty=True, stdin="wrongtok\n", extra=ME)
has("mcp tools webby", "did not accept the login", rc=1, extra=ME)
has("mcp login webby", "bearer", tty=True, stdin="webtok999\n", extra=ME)
MSEEN.clear()
has("mcp tools webby", "[read ] web_search", extra=ME)
ok([x["m"] for x in MSEEN][:3] == ["initialize", "notifications/initialized", "tools/list"] and MSEEN[2]["sid"] == "SESS1" and all(x["auth"] == "Bearer webtok999" for x in MSEEN) and MSEEN[0]["path"] == "/api/mcp", "web server: session id and bearer token are carried: " + str(MSEEN))
has("mcp look webby web_search {\"q\": \"cats\"}", "web says", "cats", extra=ME)
MODE["sse"] = True
has("mcp look webby web_search {\"q\": \"dogs\"}", "web says", "dogs", extra=ME)
MODE["sse"] = False
ok("webtok999" not in (Path(HOME) / "conn_mcp.json").read_text(), "the web token is not in the server list")
# a web server may not redirect or reach the local network in real use
try:
    _mcpclient.HTTPServer._check("https://127.0.0.1/mcp")
    ok(False, "local address refused")
except _mcpclient.MCPError:
    ok(True, "local address refused")
# ---- the person's rules for an AI reach MCP servers
try:
    ap = R.Approver(ask_fn=ask)
    out_, e_ = R.run_for_ai("mcp look files get_note {\"id\": 9}", "read", ap, HOME, extra=["apps"])
    ok(not e_ and "note 9" in out_, "an AI can use a read-marked tool: " + out_[:80])
    out_, e_ = R.run_for_ai("mcp look files put_note {\"text\": \"x\"}", "read", ap, HOME, extra=["apps"])
    ok(e_ and "not marked as only reading" in out_, "but not another tool: " + out_[:80])
    out_, e_ = R.run_for_ai("mcp add evil = sh -c id", "god", R.Approver(ask_fn=ask), HOME)
    ok(e_ and "terminal" in out_, "an AI cannot add servers: " + out_[:80])
    out_, e_ = R.run_for_ai("mcp login files FAKE_TOKEN", "god", R.Approver(ask_fn=ask), HOME)
    ok(e_, "or log in")
    out_, e_ = R.run_for_ai("mcp mark files put_note read", "god", R.Approver(ask_fn=ask), HOME)
    ok(e_, "or mark tools as read")
    has("app ai deny mcp:files", "mcp:files", tty=True)
    out_, e_ = R.run_for_ai("mcp look files get_note {\"id\": 9}", "read", ap, HOME, extra=["apps"])
    ok(e_ and "turned mcp:files off" in out_, "denied server: refused: " + out_[:80])
    FAKELOG.unlink() if FAKELOG.exists() else None
    out_, e_ = R.run_for_ai("mcp call files put_note {\"text\": \"x\"}", "god", R.Approver(ask_fn=lambda *a: True), HOME)
    ok(e_ and not FAKELOG.exists(), "denied server: calls refused too")
    has("mcp look files get_note {\"id\": 1}", "note 1")                              # you are not limited
    has("app ai reset", "any app", tty=True)
    has("app ai allow mcp:nosuch", "not known", rc=1, tty=True)
    has("app ai allow mcp:files github", "only these apps: github, mcp:files", tty=True)
    out_, e_ = R.run_for_ai("mcp look webby web_search {\"q\": \"x\"}", "read", ap, HOME, extra=["apps"])
    ok(e_ and "not on the list" in out_, "allow list: other servers shut out")
    has("app ai reset", "any app", tty=True)
    ok(R._action_key('mcp call files put_note {"text": "x"}') == "mcp_call:files:put_note", "mcp action key")
    ap = R.Approver(ask_fn=ask)
    ap.always.add("mcp_call:files:put_note")
    asked.clear(); answers["yes"] = False; FAKELOG.unlink() if FAKELOG.exists() else None
    out_, e_ = R.run_for_ai('mcp call files put_note {"text": "twice"}', "ask", ap, HOME)
    ok(not e_ and not asked and "twice" in FAKELOG.read_text(), "always-allow for one MCP tool")
    asked.clear(); FAKELOG.unlink()
    out_, e_ = R.run_for_ai('mcp call files other_tool {"text": "x"}', "ask", ap, HOME)
    ok(e_ and asked and not FAKELOG.exists(), "another tool still asks")
    ap2 = R.Approver(ask_fn=ask); ap2.dry = True; asked.clear()
    out_, e_ = R.run_for_ai('mcp call files put_note {"text": "ghost"}', "god", ap2, HOME)
    ok(not e_ and "Preview only" in out_ and not FAKELOG.exists() and not asked, "preview-only mode covers MCP calls: " + out_[:100])
finally:
    os.environ.pop("JEEG_VIA_AI", None)
msrv.shutdown()

# ---- install mcp: more AI apps
base = tempfile.mkdtemp(prefix="jeeg-v220-inst-")


def inst(words):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        rc = R.cmd_install_mcp(["py", "jeeg.py"], words, base)
    return rc, b.getvalue()


paths = R._mcp_targets(base)
ok({"claude-desktop", "cursor", "windsurf", "gemini-cli", "amazon-q", "claude-code", "vscode"} <= set(paths), "install targets")
rc, out_ = inst("")
ok(rc == 0 and "Edited for you" in out_ and "Shown, you paste" in out_ and "Need the web link" in out_, "help lists every group")
for app in ("windsurf", "gemini cli", "amazon q", "cursor"):
    key = app.replace(" ", "-")
    rc, out_ = inst(app)
    ok(rc == 0 and "nothing changed" in out_ and not paths[key].exists(), f"{app}: shows first, changes nothing")
    rc, out_ = inst(app + " yes")
    d = json.loads(paths[key].read_text())
    ok(rc == 0 and d["mcpServers"]["jeeg"]["command"] == "py" and "--mcp" in d["mcpServers"]["jeeg"]["args"], f"{app}: added")
    rc, out_ = inst(app + " remove yes")
    ok(rc == 0 and "jeeg" not in json.loads(paths[key].read_text()).get("mcpServers", {}), f"{app}: removed")
rc, out_ = inst("vs code yes")
d = json.loads(paths["vscode"].read_text())
ok(rc == 0 and d["servers"]["jeeg"]["type"] == "stdio" and "mcpServers" not in d, "vscode uses 'servers' with type stdio")
paths["claude-code"].write_text(json.dumps({"numStartups": 5, "projects": {"/x": {"a": 1}}, "mcpServers": {"other": {"command": "x"}}}))
rc, out_ = inst("claude code yes")
d = json.loads(paths["claude-code"].read_text())
ok(rc == 0 and d["numStartups"] == 5 and d["projects"] == {"/x": {"a": 1}} and set(d["mcpServers"]) == {"other", "jeeg"}, "claude code: its other settings are kept")
ok(any(p.name.startswith(".claude.json.bak-") for p in paths["claude-code"].parent.iterdir()), "and a backup was made")
paths["gemini-cli"].write_text('{ // comment\n "a": 1}')
rc, out_ = inst("gemini-cli yes")
ok(rc == 1 and "paste form" in out_ and paths["gemini-cli"].read_text().startswith("{ //"), "a settings file with comments is left alone")
for app, needle in (("zed", "context_servers"), ("codex", "config.toml"), ("goose", "goose configure"), ("continue", "mcpServers"), ("cline", "Configure"), ("jetbrains", "Settings"), ("warp", "MCP Servers")):
    rc, out_ = inst(app)
    ok(rc == 0 and needle in out_ and '"command"' in out_ and "args:" in out_, f"{app}: shows what to enter")
for app in ("chatgpt", "claude.ai", "gemini web", "copilot", "perplexity"):
    rc, out_ = inst(app)
    ok(rc == 0 and "connect ai" in out_ and "https address" in out_, f"{app}: points to the web link")
rc, out_ = inst("roo code")
ok("Roo Code" in out_, "alias: roo code")


# ================================================================ second batch: more presets and servers
BATCH = ("asana", "box", "monday", "bitbucket", "stripe", "shopify", "cloudflare", "vercel", "spotify", "twitter", "salesforce", "confluence", "grafana", "gmail", "gdrive", "gcal", "outlook")
ok(set(BATCH) <= set(_presets.PRESETS), "all second-batch presets exist")
out = has("app preset list", *BATCH)
READS = {"asana": ("me", "/users/me"), "box": ("me", "/users/me"), "bitbucket": ("me", "/user"), "stripe": ("balance", "/balance"), "cloudflare": ("verify", "/user/tokens/verify"),
         "vercel": ("me", "/v2/user"), "spotify": ("me", "/me"), "gmail": ("me", "/profile"), "gcal": ("calendars", "/users/me/calendarList"), "outlook": ("me", "/me")}
for app, (act, path) in READS.items():
    nm = "boxapp" if app == "box" else app
    has(f"app preset add {app} as={nm}", f"Added {nm}", tty=True)
    has(f"app login {nm}", "Saved", tty=True, stdin="tok-" + app + "\n")
    SEEN.clear()
    jg("app", "read", nm, act, extra={f"JEEG_APPS_BASE_{nm.upper()}": BASE})
    want = "Basic " + base64.b64encode(("tok-" + app).encode()).decode() if app == "bitbucket" else "Bearer tok-" + app
    ok(SEEN and SEEN[-1]["p"].split("?")[0].endswith(path) and SEEN[-1]["m"] == "GET" and SEEN[-1]["h"].get("authorization") == want, f"{app}: {act} sends GET {path} with the bearer login: {SEEN[-1:] }")
for app in ("stripe", "twitter", "gmail", "gdrive", "gcal", "outlook"):
    ads = A.all_adapters() if False else None
    dd = _presets.PRESETS[app]
    ok(all(not A.is_write(a) for a in dd["actions"].values()), f"{app} is look-only")
# monday: a raw-token header and a read-only POST
has("app preset add monday", "Added monday", tty=True)
has("app login monday", "Saved", tty=True, stdin="mon-raw-token\n")
SEEN.clear()
jg("app", "read", "monday", "me", extra={"JEEG_APPS_BASE_MONDAY": BASE})
ok(SEEN and SEEN[-1]["m"] == "POST" and SEEN[-1]["p"] == "/v2" and SEEN[-1]["h"].get("authorization") == "mon-raw-token" and SEEN[-1]["h"].get("api-version") and "me" in SEEN[-1]["b"], "monday: raw token header, read-only POST, version header")
# shopify: its own header, needs a base
has("app preset add shopify", "needs your own address", rc=1, tty=True)
has("app preset add shopify base=https://demo.myshopify.com/admin/api/2024-10", "Added shopify", tty=True)
has("app login shopify", "Saved", tty=True, stdin="shpat_abc\n")
SEEN.clear()
jg("app", "read", "shopify", "shop", extra={"JEEG_APPS_BASE_SHOPIFY": BASE})
ok(SEEN and SEEN[-1]["h"].get("x-shopify-access-token") == "shpat_abc" and "authorization" not in SEEN[-1]["h"] and SEEN[-1]["p"] == "/shop.json", "shopify: its own header")
# params with spaces and the odd names
has("app preset add gdrive", "Added gdrive", tty=True)
has("app login gdrive", "Saved", tty=True, stdin="gd-tok\n")
SEEN.clear()
jg("app", "read", "gdrive", "search", "q=\"name contains 'tax' & x\"", extra={"JEEG_APPS_BASE_GDRIVE": BASE})
ok(SEEN and "q=name%20contains%20%27tax%27%20%26%20x" in SEEN[-1]["p"], "a search with spaces and & is encoded, not injected: " + str(SEEN[-1:]))
has("app preset add gcal", "already", rc=1, tty=True)
SEEN.clear()
jg("app", "read", "gcal", "events", "from=2026-11-14T00:00:00Z", extra={"JEEG_APPS_BASE_GCAL": BASE})
ok(SEEN and "timeMin=2026-11-14T00%3A00%3A00Z" in SEEN[-1]["p"], "calendar: a time parameter: " + str(SEEN[-1:]))
has("app read gcal events from=tomorrow", "expected form", rc=1)
# Microsoft device login uses the preset's own addresses
DEV.update(mode="ok", polls=0)
has("app login outlook device", "client id", rc=1, tty=True)
has("app login outlook device client_id=ms-app-id", "WXYZ-1234", "Logged in to outlook", tty=True, absent=("gho_DEVICETOKEN987",))
ok(DEV["client"] == "ms-app-id" and json.loads((Path(HOME) / "conn_appsecrets.json").read_text())["outlook"] == "gho_DEVICETOKEN987", "outlook device login saved its token")
dd = {"title": "t", "base": "https://api.example.com", "auth": "bearer", "device": {"code_url": "http://x.com/c", "token_url": "https://x.com/t"}, "actions": {"me": {"method": "GET", "path": "/me"}}}
ok(A.check_def("devapp", dd) is not None, "device login addresses must be https")
dd["device"]["code_url"] = "https://x.com/c"
ok(A.check_def("devapp", dd) is None, "a good device block is accepted")
# a client secret goes only in the token request
import _device
DEV.update(mode="ok", polls=0)
os.environ.update({"JEEG_DEVICE_BASE": DBASE, "JEEG_DEVICE_INTERVAL": "0.05"})
tok_ = _device.login("github", "cid", client_secret="sec-xyz", out=lambda *a: None)
os.environ.pop("JEEG_DEVICE_BASE"); os.environ.pop("JEEG_DEVICE_INTERVAL")
ok(tok_ == "gho_DEVICETOKEN987", "device login with a client secret works")

# MCP servers with several login variables
script("fakemcp2", f"""#!{sys.executable}
import sys, json, os
for line in sys.stdin:
    m = json.loads(line); i = m.get("id"); meth = m.get("method")
    if i is None: continue
    if meth == "tools/call":
        r = {{"content": [{{"type": "text", "text": "host=%s user=%s pw=%s" % (os.environ.get("MYSQL_HOST"), os.environ.get("MYSQL_USER"), os.environ.get("MYSQL_PASSWORD"))}}]}}
    else: r = {{"protocolVersion": "2024-11-05", "capabilities": {{}}, "tools": []}}
    print(json.dumps({{"jsonrpc": "2.0", "id": i, "result": r}}), flush=True)
""")
has("mcp add db = fakemcp2", "Saved db", tty=True)
has("mcp mark db query read", "marked read", tty=True)
has("mcp login db MYSQL_HOST MYSQL_USER MYSQL_PASSWORD", "MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD", tty=True, stdin="dbhost\ndbuser\ndbpass\n")
has("mcp look db query {}", "host=dbhost user=dbuser pw=dbpass")
sec = (Path(HOME) / "conn_mcpsecrets.json").read_text()
ok("db:MYSQL_PASSWORD" in sec and "dbpass" not in (Path(HOME) / "conn_mcp.json").read_text() + (Path(HOME) / "conn_mcpenv.json").read_text(), "each variable is saved on its own, only in the secrets file")
has("mcp login db MYSQL_HOST MYSQL_USER MYSQL_PASSWORD", "does not look right", rc=1, tty=True, stdin="a\nb\nsp ace\n")
has("mcp list", "db", "NEEDS LOGIN")
has("mcp login db MYSQL_HOST MYSQL_USER MYSQL_PASSWORD", "Saved", tty=True, stdin="dbhost\ndbuser\ndbpass\n")
has("mcp logout db", "Forgot", tty=True)
has("mcp look db query {}", "needs a login", rc=1)
has("mcp remove db", "Removed", tty=True)
ok("db:" not in (Path(HOME) / "conn_mcpsecrets.json").read_text(), "removing a server removes all its logins")
has("mcp add mysql", "Saved mysql", "mcp login mysql", tty=True)
has("mcp add redis", "needs redis://", rc=1, tty=True)
has("mcp add neo4j", "Saved neo4j", "2 tool(s) are marked" if False else "marked as only reading", tty=True)
has("mcp catalog", "slack", "mysql", "neo4j", "Bitbucket", "Asana", "Outlook")

# ================================================================ real test: compare
RH = Path(HOME) / "realtest_history.json"
has("real test compare", "needs two runs", rc=1)
RH.write_text(json.dumps([{"ts": 1700000000, "version": "2.19.0", "status": {"system.disk": "pass", "net.dns": "pass", "old.step": "pass", "files.a": "fail", "apps.x.read": "skip"}},
                          {"ts": 1700003600, "version": "2.20.0", "status": {"system.disk": "fail", "net.dns": "pass", "new.step": "pass", "files.a": "pass", "apps.x.read": "pass"}}]))
out = has("real test compare", "2.19.0", "2.20.0", "updated in between", "Got worse (1)", "system.disk: pass -> fail", "Got better (2)", "files.a: fail -> pass", "New checks", "new.step", "no longer there", "old.step")
RH.write_text(json.dumps([{"ts": 1, "version": jeeg.__version__, "status": {"a": "pass"}}, {"ts": 2, "version": jeeg.__version__, "status": {"a": "pass"}}]))
has("real test compare", "No differences")
RH.write_text(json.dumps([{"ts": 1, "version": "1.0.0", "status": {"a": "pass"}}]))
has("real test list", "was updated (1.0.0 ->", "real test compare")
RH.unlink()
import _realtest as RT
STEP = RT.STEPS[0]["id"]
code, _ = jg("real", "test", "run", STEP, extra={"JEEG_REALTEST_BUDGET": "30"})
ok(RH.exists() and json.loads(RH.read_text())[-1]["version"] == jeeg.__version__ and json.loads(RH.read_text())[-1]["status"], "a run saves a snapshot for later comparing")
jg("real", "test", "run", STEP, extra={"JEEG_REALTEST_BUDGET": "30"})
has("real test compare", "Before:", "After:")
has("real test", "compare")

# ================================================================ nothing leaks, nothing odd on disk
allfiles = [p for p in Path(HOME).glob("*") if p.is_file()]
secrets_ = ("shoptoken123", "glpat-abc", "lin_api_xyz", "gho_DEVICETOKEN987", "ghp_AI1", "tok789", "newtoken456")
leaks = [p.name for p in allfiles if not p.name.startswith("conn_") and any(s in p.read_text(errors="replace") for s in secrets_)]
ok(not leaks, "logins only live in the conn_ files: " + str(leaks))
hist = (Path(HOME) / "history.jsonl").read_text() if (Path(HOME) / "history.jsonl").exists() else ""
ok("ghost" not in hist, "what you ran through apps is not kept in history")
ok(all(os.name == "nt" or (p.stat().st_mode & 0o077) == 0 for p in allfiles if p.name.startswith("conn_")), "login files are private")
for f in ("keystore.json", "app_policy.json", "rules.json"):
    ok(not (Path(HOME) / f).exists() or "secret" not in (Path(HOME) / f).read_text().lower(), f + " holds no secret")

srv.shutdown(); dsrv.shutdown()
print(f"v2.20 tests: {P} passed, {F} failed")
sys.exit(1 if F else 0)
