"""v2.18: linked apps (app adapters). Everything runs against this computer: a fake app server stands in for GitHub, Telegram, Discord and a custom app.
Run: python tests/test_v218.py"""
import http.server, json, os, re, stat, subprocess, sys, tempfile, threading, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
HOME = tempfile.mkdtemp(prefix="jeeg-v218-")
WORK = Path(tempfile.mkdtemp(prefix="jeeg-v218-w-"))
os.environ["JEEG_HOME"] = HOME
P = F = 0


def ok(c, label):
    global P, F
    if c:
        P += 1
    else:
        F += 1
        print("FAIL:", label)


# ------------------------------------------------------------------ fake servers: the "app" and a second site that must never be contacted
SEEN, OTHER = [], []


class App(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _do(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n).decode() if n else ""
        SEEN.append({"m": self.command, "p": self.path, "h": {k.lower(): v for k, v in self.headers.items()}, "b": body})
        path = self.path.split("?")[0]
        if path.endswith("/redir"):
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{other.server_address[1]}/stolen")
            self.end_headers()
            return
        if path.endswith("/boom"):
            self.send_error(500)
            return
        if path.endswith("/denied"):
            self.send_response(401)
            self.end_headers()
            return
        data = {
            "/issues": [{"number": 7, "title": "Crash on start", "repository": {"full_name": "me/app"}}, {"number": 9, "title": "Add dark mode\x1b[31m<script>", "repository": {"full_name": "me/site"}}],
            "/user": {"login": "asha", "name": "Asha Rao"},
            "/repos/o/r/issues": [{"number": 1, "title": "First", "user": {"login": "bob"}}],
            "/repos/o/r/issues/3/comments": {"html_url": "https://github.com/o/r/issues/3#c1"},
            "/api/items": {"items": [{"id": 1, "name": "pen"}, {"id": 2, "name": "book"}]},
            "/api/plain": "just some text",
        }.get(path)
        if self.command == "POST" and path.startswith("/api/items"):
            data = {"id": 3, "name": json.loads(body or "{}").get("name")}
        if path.endswith("/getMe"):
            data = {"result": {"first_name": "Helper", "username": "helper_bot"}}
        if path.endswith("/sendMessage") or path.startswith("/hook"):
            data = {"ok": True}
        if data is None:
            self.send_error(404)
            return
        b = (data if isinstance(data, str) else json.dumps(data)).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json" if not isinstance(data, str) else "text/plain")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _do


class Other(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        OTHER.append(dict(self.headers))
        self.send_response(200)
        self.end_headers()


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), App)
other = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Other)
for s in (srv, other):
    threading.Thread(target=s.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}"
BIN = Path(tempfile.mkdtemp(prefix="jeeg-v218-bin-"))
fb = BIN / "fakebrowser.sh"
fb.write_text(f'#!/bin/sh\necho "$1" >> {WORK}/browser_urls\n')
fb.chmod(fb.stat().st_mode | stat.S_IXUSR)
TOKEN, TG, HOOK = "ghp_TESTTOKEN1234567890", "123456:AAEtelegramSECRETtoken", "https://discord.com/api/webhooks/111/SECRETHOOKPART"


def env(extra=None):
    e = dict(os.environ, JEEG_HOME=HOME, NO_PROXY="127.0.0.1,localhost", no_proxy="127.0.0.1,localhost", BROWSER=str(fb) + " %s",
             JEEG_APPS_BASE_GITHUB=BASE, JEEG_APPS_BASE_TELEGRAM=BASE + "/bot{secret}", JEEG_APPS_BASE_DISCORD=BASE + "/hook")
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
        e.pop(k, None)
    e.update(extra or {})
    return e


def jg(*words, yes=False, tty=False, stdin="", extra=None):
    e = env(extra)
    if tty:
        e["JEEG_TEST_TTY"] = "1"
    a = [sys.executable, str(ROOT / "jeeg.py")] + (["--yes"] if yes else []) + list(words)
    r = subprocess.run(a, capture_output=True, text=True, timeout=60, env=e, cwd=WORK, input=stdin)
    return r.returncode, r.stdout + r.stderr


def has(q, *needles, rc=0, absent=(), **kw):
    code, out = jg(q, **kw)
    ok(code == rc and all(n in out for n in needles) and not any(a in out for a in absent), f"{q!r} -> rc={code} {out.strip()[:260]!r}")
    return out


def sent():
    n = len(SEEN)
    return n


import jeeg
ok(tuple(int(x) for x in jeeg.__version__.split(".")) >= (2, 18, 0), "version " + jeeg.__version__)
import _adapters as A

# ================================================================ definitions are checked
for n, d in A.BUILTIN.items():
    ok(A.check_def(n, d) is None, f"builtin {n} is valid: {A.check_def(n, d)}")
good = {"title": "x", "base": "https://api.example.com/v1", "auth": "bearer", "actions": {"list": {"method": "GET", "path": "/things"}}}
ok(A.check_def("shop", good) is None, "a plain definition is accepted")


def bad(label, mutate, name="shop"):
    import copy
    d = copy.deepcopy(good)
    mutate(d)
    ok(A.check_def(name, d) is not None, "rejected: " + label)


bad("name with caps", lambda d: None, "Shop")
bad("name too short", lambda d: None, "x")
bad("name with space", lambda d: None, "my shop")
bad("public http", lambda d: d.update(base="http://api.example.com"))
bad("user:password in address", lambda d: d.update(base="https://u:p@api.example.com"))
bad("ftp address", lambda d: d.update(base="ftp://api.example.com"))
bad("placeholder in host", lambda d: d.update(base="https://{x}.example.com"))
bad("unknown login style", lambda d: d.update(auth="magic"))
bad("header login without a name", lambda d: d.update(auth="header"))
bad("path_token without {secret}", lambda d: d.update(auth="path_token"))
bad("path with ..", lambda d: d["actions"]["list"].update(path="/a/../b"))
bad("path to another site", lambda d: d["actions"]["list"].update(path="https://evil.example.com/x"))
bad("path not starting with /", lambda d: d["actions"]["list"].update(path="things"))
bad("TRACE method", lambda d: d["actions"]["list"].update(method="TRACE"))
bad("undeclared placeholder in path", lambda d: d["actions"]["list"].update(path="/a/{who}"))
bad("undeclared placeholder in body", lambda d: d["actions"]["list"].update(method="POST", body={"a": "{who}"}))
bad("action name with caps", lambda d: d["actions"].update({"Bad": {"method": "GET", "path": "/x"}}))
bad("Authorization header", lambda d: d.update(headers={"Authorization": "x"}))
bad("Cookie header", lambda d: d.update(headers={"Cookie": "x"}))
bad("header with newline", lambda d: d.update(headers={"X-A": "a\nb"}))
bad("too many actions", lambda d: d.update(actions={f"a{i}": {"method": "GET", "path": "/x"} for i in range(41)}))
bad("broken regex", lambda d: d["actions"]["list"].update(params={"q": {"pat": "("}}))
bad("open action over http", lambda d: d["actions"].update({"o": {"kind": "open", "url": "http://x.example.com/{q}", "params": {"q": {}}}}))
ok(A.check_def("local", {**good, "base": "http://192.168.1.5:8123/api"}) is None and A.check_def("local", {**good, "base": "http://127.0.0.1:8123"}) is None, "http is fine on this computer and the home network")
ok(not A.is_write({"method": "GET"}) and not A.is_write({"method": "HEAD"}) and A.is_write({"method": "POST"}) and A.is_write({"method": "DELETE"}) and A.is_write({"kind": "open"}), "only GET/HEAD are reads")
ok(A.all_adapters()["github"][1] is True, "builtin flagged")

# ================================================================ arguments
gh = A.BUILTIN["github"]["actions"]
v, why = A.parse_args(gh["repo_issues"], "o/r")
ok(v == {"repo": "o/r"} and why is None, "positional")
v, why = A.parse_args(gh["comment"], "repo=o/r number=3 looks good to me")
ok(v == {"repo": "o/r", "number": "3", "text": "looks good to me"}, "named + free text: " + str(v))
v, why = A.parse_args(gh["comment"], 'text="two words, ok" repo=o/r number=3')
ok(v and v["text"] == "two words, ok", "quoted value")
v, why = A.parse_args(gh["comment"], "o/r 3 hello there")
ok(v == {"repo": "o/r", "number": "3", "text": "hello there"}, "all positional")
v, why = A.parse_args(gh["comment"], "repo=o/r number=3")
ok(v is None and "text" in why, "missing parameter named: " + str(why))
v, why = A.parse_args(gh["comment"], "repo=o/r number=abc hi")
ok(v is None and "number" in why, "pattern enforced")
v, why = A.parse_args(gh["comment"], "repo=../etc number=3 hi")
ok(v is None, "bad repo refused")
v, why = A.parse_args(gh["repo_issues"], "a/../b")
ok(v is None, "dot-dot refused")
v, why = A.parse_args(gh["repo_issues"], "a/b/c")
ok(v is None, "too many slashes refused")
v, why = A.parse_args(gh["create_issue"], "repo=o/r title=Hello")
ok(v == {"repo": "o/r", "title": "Hello", "text": ""}, "optional parameter may be empty: " + str(v))
v, why = A.parse_args(gh["me"], "")
ok(v == {} and why is None, "no parameters")
v, why = A.parse_args(gh["me"], "surprise")
ok(v is None, "unexpected arguments refused")
wa = A.BUILTIN["whatsapp"]["actions"]["message"]
v, why = A.parse_args(wa, 'phone="+91 98765-43210" text="hi there"')
ok(v == {"phone": "919876543210", "text": "hi there"}, "phone digits cleaned: " + str(v))
v, why = A.parse_args(wa, "phone=12 text=hi")
ok(v is None, "short phone refused")
v, why = A.parse_args(wa, "phone=9198765432 text=a\x07b")
ok(v is None, "control characters refused")

# ================================================================ requests are built safely
req = A.build("github", A.BUILTIN["github"], "repo_issues", {"repo": "o/r"}, "tok")
ok(req["url"] == "https://api.github.com/repos/o/r/issues?state=open&per_page=15" and req["method"] == "GET" and req["headers"]["Authorization"] == "Bearer tok", "github url+auth: " + req["url"])
evil = 'x"}, "labels": ["admin"], "y": "\n'
req = A.build("github", A.BUILTIN["github"], "comment", {"repo": "o/r", "number": "3", "text": evil}, "tok")
ok(json.loads(req["body"]) == {"body": evil} and req["method"] == "POST" and req["headers"]["Content-Type"] == "application/json", "body text cannot break out of its JSON string")
req = A.build("github", A.BUILTIN["github"], "comment", {"repo": "o/r", "number": "3?x=1#frag", "text": "t"}, "tok")
ok("%3F" in req["url"] and "#" not in req["url"].split("comments")[0] and req["url"].count("?") == 0, "path values are encoded: " + req["url"])
req = A.build("telegram", A.BUILTIN["telegram"], "send", {"chat": "12", "text": "hi"}, "123:ABC")
ok(req["url"] == "https://api.telegram.org/bot123:ABC/sendMessage" and json.loads(req["body"]) == {"chat_id": "12", "text": "hi"}, "telegram token goes in the path: " + req["url"])
req = A.build("discord", A.BUILTIN["discord"], "send", {"text": "yo"}, HOOK)
ok(req["url"] == HOOK and "Authorization" not in req["headers"], "webhook address is the secret")
req = A.build("whatsapp", A.BUILTIN["whatsapp"], "message", {"phone": "919876543210", "text": "hi & bye? #1"}, "")
ok(req["method"] == "OPEN" and req["url"] == "https://wa.me/919876543210?text=hi%20%26%20bye%3F%20%231", "whatsapp link quoted: " + req["url"])
for auth, extra, check in (("header", {"header": "X-Key"}, lambda r: r["headers"].get("X-Key") == "S3CRET"), ("query", {"header": "key"}, lambda r: r["url"].endswith("?key=S3CRET")),
                           ("basic", {}, lambda r: r["headers"]["Authorization"].startswith("Basic ")), ("none", {}, lambda r: "Authorization" not in r["headers"])):
    d = {**good, "auth": auth, **extra}
    ok(A.check_def("shop", d) is None and check(A.build("shop", d, "list", {}, "S3CRET")), "login style " + auth)
d = {**good, "headers": {"X-App": "1"}}
ok(A.build("shop", d, "list", {}, "S")["headers"]["X-App"] == "1", "static header sent")
d = {**good, "actions": {"find": {"method": "GET", "path": "/s", "query": {"q": "{q}"}, "params": {"q": {}}}}}
ok(A.build("shop", d, "find", {"q": "a&b=c d"}, "S")["url"].endswith("/s?q=a%26b%3Dc+d"), "query values are encoded")
ok(A.scrub("see ghp_X and ghp_X%20 now", "ghp_X").count("ghp_X") == 0, "secret scrubbed")
ok("\x1b" not in A.scrub("a\x1b[31mb", ""), "control characters scrubbed")

# ================================================================ showing results
ok(A.render({"format": "{n}: {t.u}", "list": "items"}, json.dumps({"items": [{"n": 1, "t": {"u": "x"}}, {"n": 2}]})) == "1: x\n2:", "list + nested fields")
ok(A.render({}, "plain\x1b[1m text") == "plain[1m text", "non-JSON text shown, control chars removed")
ok(A.render({"format": "{a}"}, "[]") == "(nothing)", "empty list")
big = A.render({"format": "{a}"}, json.dumps([{"a": i} for i in range(40)]))
ok(big.count("\n") == 25 and "15 more" in big, "long lists are cut at 25")
ok(A.render({"format": "sent"}, '{"ok":true}') == "Sent.", "sent")
ok(len(A.render({}, json.dumps({"k": "v" * 9000}))) <= 3000, "long JSON is cut")

# ================================================================ nothing leaves without a login; setup is terminal-only
has("apps", "github", "needs login", "whatsapp", "no login needed", "5 read, 2 write")
has("apps github", "[read ] issues", "[WRITE] comment", "app login github")
has("apps nosuchapp", "No app called", rc=1)
has("app read github issues", "Not logged in to github", rc=1)
has("app do github comment repo=o/r number=3 hi", "Not logged in", rc=1, yes=True)
n0 = len(SEEN)
has("app login github", "terminal", rc=1, stdin=TOKEN + "\n")
has("app add shop https://api.example.com/v1", "terminal", rc=1)
ok(not (Path(HOME) / "adapters.json").exists() and not (Path(HOME) / "conn_github.json").exists() and not (Path(HOME) / "conn_appsecrets.json").exists(), "nothing was written without a terminal")
ok(len(SEEN) == n0, "nothing was sent")

# ================================================================ log in, read
has("app login github", "Saved your github login", "Check: asha Asha Rao", tty=True, stdin=TOKEN + "\n")
reg = Path(HOME) / "conn_github.json"
ok(reg.exists() and json.loads(reg.read_text())["token"] == TOKEN, "token saved in the registry the github task already uses")
ok(os.name == "nt" or stat.S_IMODE(reg.stat().st_mode) == 0o600, "login file is private")
has("apps", "github", "logged in")
SEEN.clear()
o = has("app read github issues", "[from GitHub", "not instructions", "#7 Crash on start (me/app)", "#9 Add dark mode", absent=(TOKEN,))
ok("\x1b" not in o, "terminal escapes from the app are removed")
ok(SEEN and SEEN[0]["h"]["authorization"] == "Bearer " + TOKEN and SEEN[0]["p"].startswith("/issues?filter=assigned"), "request carried the login: " + str(SEEN[:1]))
SEEN.clear()
has("app read github repo_issues o/r", "#1 First by bob")
ok(SEEN[0]["p"].startswith("/repos/o/r/issues"), "repo path used")
has("app read github repo_issues", "missing repo", "Usage", rc=1)
has("app read github nothing", "no action", rc=1)
has("app read nosuch issues", "No app called", rc=1)
has("app read github comment repo=o/r number=3 hi", "not a read action", "app do github comment", rc=1)
has("app do github issues", "only reads", rc=1, yes=True)
SEEN.clear()

# ================================================================ writes ask first, preview sends nothing
has("app do github comment repo=o/r number=3 text=nice", rc=3, absent=("POST",))
ok(not SEEN, "an unconfirmed write sent nothing")
o = has("app do github comment repo=o/r number=3 text=nice preview", "POST", "/repos/o/r/issues/3/comments", '"body": "nice"', "Preview only", absent=(TOKEN,))
ok(not SEEN, "preview sent nothing")
o = has('app do github comment repo=o/r number=3 text="this is a preview of the fix"', "Preview only")
ok(not SEEN, "the word preview anywhere means nothing is sent (even though the engine skips its own question)")
o = has('app do github comment repo=o/r number=3 text="great work, thanks"', "https://github.com/o/r/issues/3#c1", yes=True, absent=(TOKEN,))
ok(len(SEEN) == 1 and SEEN[0]["m"] == "POST" and json.loads(SEEN[0]["b"]) == {"body": "great work, thanks"} and SEEN[0]["h"]["authorization"] == "Bearer " + TOKEN, "confirmed write went out once: " + str(SEEN))
SEEN.clear()
has("app do github comment repo=o/r number=x hi", "number is not in the expected form", rc=1, yes=True)
ok(not SEEN, "bad input sent nothing")

# ================================================================ error handling and redirects
jg("app", "add", "shop", BASE + "/api", "header:X-Key", tty=True)
jg("app", "action", "shop", "list", "GET", "/items", 'list=items', 'format={id}: {name}', "desc=all items", tty=True)
jg("app", "action", "shop", "plain", "GET", "/plain", tty=True)
jg("app", "action", "shop", "add", "POST", "/items", "params=name", 'body={"name":"{name}"}', tty=True)
jg("app", "action", "shop", "redir", "GET", "/redir", tty=True)
jg("app", "action", "shop", "boom", "GET", "/boom", tty=True)
jg("app", "action", "shop", "denied", "GET", "/denied", tty=True)
has("app login shop", "Saved your shop login", tty=True, stdin="shopsecretkey99\n")
SEEN.clear()
has("app read shop list", "1: pen", "2: book", absent=("shopsecretkey99",))
ok(SEEN[0]["h"].get("x-key") == "shopsecretkey99" and SEEN[0]["p"] == "/api/items", "custom header login and path: " + str(SEEN[:1]))
has("app read shop plain", "just some text")
SEEN.clear(); OTHER.clear()
has("app read shop redir", "redirected", "never sent elsewhere", rc=1, absent=("shopsecretkey99",))
ok(not OTHER, "the redirect target was never contacted: " + str(OTHER))
has("app read shop boom", "HTTP 500", rc=1)
has("app read shop denied", "refused the login", rc=1)
SEEN.clear()
has("app do shop add name=ruler", "Done (HTTP 200)", yes=True)
ok(SEEN and json.loads(SEEN[0]["b"]) == {"name": "ruler"} and SEEN[0]["m"] == "POST" and SEEN[0]["h"]["x-key"] == "shopsecretkey99", "custom write went out")
has("apps shop", "[read ] list", "[WRITE] add", "all items")

# ================================================================ defining apps is checked
has("app add shop https://x.example.com", "already an app", rc=1, tty=True)
has("app add github https://x.example.com", "already an app", rc=1, tty=True)
has("app add evil http://api.example.com/v1", "plain http", rc=1, tty=True)
has("app add evil https://u:p@api.example.com", rc=1, tty=True)
has("app add Ev!l https://api.example.com", "letters, numbers", rc=1, tty=True)
has("app add evil https://api.example.com magic", "Login style", rc=1, tty=True)
has("app action github hack GET /x", "built in", rc=1, tty=True)
has("app action shop bad TRACE /x", "method", rc=1, tty=True)
has("app action shop bad GET https://evil.example.com/x", rc=1, tty=True)
has("app action shop bad GET /a/{who}", "not declared", rc=1, tty=True)
has('app action shop bad POST /x body={"a":"{who}"}', rc=1, tty=True)
has("app action shop bad POST /x body=notjson", "valid JSON", rc=1, tty=True)
has("app action shop bad GET /x color=red", "do not know", rc=1, tty=True)
has("app action shop bad GET /x color red", "do not know", rc=1, tty=True)
has("app action shop bad GET /x params=a:weird", "not known", rc=1, tty=True)
has("app login shop", "does not look like a token", rc=1, tty=True, stdin="has spaces in it\n")
has("app login discord", "does not look like a discord", rc=1, tty=True, stdin="https://evil.example.com/hook\n")
has("app login slack", "full webhook address", rc=1, tty=True, stdin="notaurl\n")
u = json.loads((Path(HOME) / "adapters.json").read_text())
ok(set(u) == {"shop"} and all(a["method"] in A.METHODS for a in u["shop"]["actions"].values()), "only valid definitions were saved")
(Path(HOME) / "adapters.json").write_text(json.dumps({**u, "broken": {"title": "x", "base": "http://public.example.com", "auth": "none", "actions": {"a": {"method": "GET", "path": "/"}}}, "github": {"title": "hijack"}}))
ok("broken" not in A.all_adapters() and A.all_adapters()["github"][0]["title"] == "GitHub", "a hand-edited bad file cannot add a broken app or replace a built-in one")
(Path(HOME) / "adapters.json").write_text(json.dumps(u))

# ================================================================ telegram, discord, whatsapp
has("app login telegram", "Saved your telegram login", "Check: Helper (@helper_bot)", tty=True, stdin=TG + "\n", absent=(TG,))
SEEN.clear()
o = has("app do telegram send chat=555 hello from jeeg preview", "sendMessage", "***", "Preview only", absent=(TG,))
ok(not SEEN, "telegram preview sent nothing")
o = has("app do telegram send chat=555 hello from jeeg", "Sent.", yes=True, absent=(TG,))
ok(SEEN and SEEN[-1]["p"] == "/bot" + urllib.parse.quote(TG, safe=":") + "/sendMessage" and json.loads(SEEN[-1]["b"]) == {"chat_id": "555", "text": "hello from jeeg"}, "telegram message went out: " + str(SEEN[-1:]))
has("app do telegram send chat=not-a-chat hi", "chat is not in the expected form", rc=1, yes=True)
has("app login discord", "Saved your discord login", tty=True, stdin=HOOK + "\n", absent=("SECRETHOOKPART",))
SEEN.clear()
o = has("app do discord send ship it", "Sent.", yes=True, absent=("SECRETHOOKPART",))
ok(SEEN and SEEN[0]["p"] == "/hook" and json.loads(SEEN[0]["b"]) == {"content": "ship it"}, "discord message went out")
o = has('app do whatsapp message phone="+91 98765 43210" text="hi there" preview', "https://wa.me/919876543210?text=hi%20there", "Preview only")
ok(not (WORK / "browser_urls").exists(), "preview opened nothing")
has('app do whatsapp message phone="+91 98765 43210" text="hi there"', rc=3)
o = has('app do whatsapp message phone="+91 98765 43210" text="hi there"', "Press Send", yes=True)
import time
for _ in range(20):
    if (WORK / "browser_urls").exists():
        break
    time.sleep(0.1)
ok((WORK / "browser_urls").exists() and "https://wa.me/919876543210?text=hi%20there" in (WORK / "browser_urls").read_text(), "the chat was opened with the message typed in")

# ================================================================ nothing secret leaks anywhere else
allfiles = [p for p in Path(HOME).rglob("*") if p.is_file()]
leaks = [p.name for p in allfiles if not p.name.startswith("conn_") and any(s in p.read_text(errors="replace") for s in (TOKEN, TG, "SECRETHOOKPART", "shopsecretkey99"))]
ok(not leaks, "secrets only live in the conn_ files: " + str(leaks))
ok(all(os.name == "nt" or stat.S_IMODE(p.stat().st_mode) == 0o600 for p in allfiles if p.name.startswith("conn_")), "all login files are private")
hist = (Path(HOME) / "history.jsonl").read_text() if (Path(HOME) / "history.jsonl").exists() else ""
ok("great work, thanks" not in hist and "hello from jeeg" not in hist and "ship it" not in hist, "what you sent through apps is not kept in history")

# ================================================================ log out, remove
has("app logout github", "Logged out of github", tty=True)
has("app logout github", "not logged in", tty=True)
has("app read github issues", "Not logged in", rc=1)
ok("token" not in json.loads(reg.read_text()), "token deleted")
has("app remove github", "built in", rc=1, tty=True)
has("app remove shop", "Removed shop", tty=True)
has("app read shop list", "No app called", rc=1)
ok("shop" not in json.loads((Path(HOME) / "conn_appsecrets.json").read_text()), "its login was deleted too")

# ================================================================ AI mode: reads need your opt-in, writes ask, setup is impossible
import jeeg_remote as R
asked = []
answers = {"yes": True}


def ask(text, *a):
    asked.append(text)
    return answers["yes"]


jg("app", "login", "github", tty=True, stdin=TOKEN + "\n")
os.environ.update({k: v for k, v in env().items() if k.startswith("JEEG_APPS_BASE_") or k in ("NO_PROXY", "no_proxy", "BROWSER")})
for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(k, None)
ap = R.Approver(ask_fn=ask)
SEEN.clear()
out, err = R.run_for_ai("app read github issues", "safe", ap, HOME)
ok(err and not SEEN, "safe mode cannot read your apps: " + out[:100])
out, err = R.run_for_ai("app read github issues", "read", ap, HOME)
ok(err and not SEEN, "read mode does not reach your apps unless you allow them: " + out[:100])
out, err = R.run_for_ai("app read github issues", "read", ap, HOME, extra=["apps"])
ok(not err and "Crash on start" in out and SEEN, "read mode + 'allow apps' can read: " + out[:100])
SEEN.clear()
out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=sneaky", "read", ap, HOME, extra=["apps"])
ok(err and not SEEN, "'allow apps' never lets the AI write: " + out[:100])
out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=sneaky", "safe", ap, HOME)
ok(err and not SEEN, "safe mode cannot write")
asked.clear(); answers["yes"] = False
out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=sneaky", "ask", ap, HOME)
ok(err and not SEEN and asked, "ask mode: a 'no' sends nothing: " + out[:100])
asked.clear(); answers["yes"] = True
out, err = R.run_for_ai("app do github comment repo=o/r number=3 text=approved", "ask", ap, HOME)
ok(not err and len(SEEN) == 1 and json.loads(SEEN[0]["b"]) == {"body": "approved"} and len(asked) >= 2, f"ask mode: yes (and the confirmation) sends it: {out[:100]} asked={len(asked)}")
SEEN.clear()
before = (Path(HOME) / "adapters.json").read_text()
for q in ("app add evil https://evil.example.com bearer", "app action shop x GET /x", "app login github", "app remove shop", "app logout github"):
    out, err = R.run_for_ai(q, "god", R.Approver(ask_fn=ask), HOME)
    ok(err and "terminal" in out.lower(), f"god mode cannot run {q!r}: {out[:100]}")
ok((Path(HOME) / "adapters.json").read_text() == before and json.loads(reg.read_text()).get("token") == TOKEN, "the AI changed no app and no login")
ok("Apps the person linked" in (ROOT / "jeeg_remote.py").read_text(encoding="utf-8"), "the AI is told about linked apps")

srv.shutdown(); other.shutdown()
print(f"v2.18 tests: {P} passed, {F} failed")
sys.exit(1 if F else 0)
