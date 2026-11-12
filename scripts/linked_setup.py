# keywords: app login, app logout, app add, app action, app remove, link app, connect app, add my own app
# desc: Link JeeG to an app: log in (app login github), add your own app by its web address (app add trello https://api.trello.com/1 query:key), define what it can do (app action ...), log out or remove. Terminal only: an AI cannot do this.
# category: apps_setup
# usage: app login <app> | app logout <app> | app add <name> <https://base> [none|bearer|basic|header:NAME|query:NAME] | app action <app> <name> <GET|POST|...> </path> [params=a,b] [format="{x}"] [list=path] [body='{"k":"{a}"}'] [desc="..."] | app remove <name>
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*(?:app|linked)\s+(?:login|logout|add|action|remove)\b
# priority: 5
import json, os, re, sys
from _adapters import (AUTHS, METHODS, NAME, all_adapters, build, check_def, check_secret, drop_secret, get_secret, is_write, parse_args, render, send,
                       set_secret, user_defs)
from _conn import ask_secret
from _lib import args_text, fail
from _store import save

if not (sys.stdin is not None and sys.stdin.isatty()) and os.environ.get("JEEG_TEST_TTY") != "1":
    fail("Linking apps is done by you, in a terminal window, so a program or an AI cannot change it. Open a terminal and run the same words there.")
text = args_text().strip()
m = re.match(r"^(?:app|linked)\s+(login|logout|add|action|remove)\b\s*(.*)$", text, re.I | re.S)
if not m:
    fail("Try:  app login github     |     app add <name> <https://base> [bearer]     |     app action <app> <name> GET /path")
cmd, rest = m.group(1).lower(), m.group(2).strip()
toks = rest.split()
ads = all_adapters()


def need_app(n, mine_only=False):
    n = (n or "").lower()
    if n not in ads:
        fail(f"No app called '{n}'. See:  apps")
    if mine_only and ads[n][1]:
        fail(f"{n} is built in and cannot be changed. You can add your own app under another name.")
    return n, ads[n][0]


if cmd in {"login", "logout"}:
    n, d = need_app(toks[0] if toks else "")
    if d["auth"] == "none":
        print(f"{n} needs no login.  {d.get('login_help', '')}")
        raise SystemExit(0)
    if cmd == "logout":
        print(f"Logged out of {n}." if drop_secret(n, d) else f"You were not logged in to {n}.")
        raise SystemExit(0)
    if d.get("login_help"):
        print(d["login_help"])
    s = ask_secret(f"Paste the {'webhook address' if d['auth'] == 'url' else 'token'} for {n} (nothing is shown; it stays on this computer): ")
    why = check_secret(d, s)
    if why:
        fail(why)
    set_secret(n, d, s)
    print(f"Saved your {n} login (private to you, in a file only your user can read).")
    act = d["actions"].get("me")
    if act and not is_write(act):
        try:
            _, out = send(build(n, d, "me", {}, s), s)
            print("Check: " + render(act, out, s))
        except RuntimeError as ex:
            print(f"Saved, but the check failed: {ex}")
    raise SystemExit(0)
if cmd == "remove":
    n, d = need_app(toks[0] if toks else "", True)
    u = user_defs()
    u.pop(n, None)
    save("adapters.json", u)
    drop_secret(n, d)
    print(f"Removed {n} and its login.")
    raise SystemExit(0)
if cmd == "add":
    if len(toks) < 2:
        fail("Usage:  app add <name> <https://api.example.com/v1> [none|bearer|basic|header:NAME|query:NAME]")
    n = toks[0].lower()
    if n in ads:
        fail(f"There is already an app called {n}.")
    auth, header = (toks[2].lower() if len(toks) > 2 else "bearer"), ""
    if ":" in auth:
        auth, header = auth.split(":", 1)
    if auth not in AUTHS - {"path_token", "url"}:
        fail("Login style: none, bearer, basic, header:NAME or query:NAME")
    d = {"title": n, "base": toks[1].rstrip("/"), "auth": auth, "actions": {}}
    if header:
        d["header"] = header
    why = check_def(n, d)
    if why:
        fail(why)
    if len(user_defs()) >= 30:
        fail("That is 30 apps already.")
    u = user_defs()
    u[n] = d
    save("adapters.json", u)
    print(f"Added {n}. Next, say what it can do, for example:\n  app action {n} boards GET /members/me/boards format=\"{{name}}\"\n" + (f"and log in:  app login {n}" if auth != "none" else ""))
    raise SystemExit(0)
# action
if len(toks) < 4:
    fail('Usage:  app action <app> <name> <GET|POST|PUT|PATCH|DELETE> </path> [params=a,b] [format="{field}"] [list=path.to.list] [body=\'{"k":"{a}"}\'] [desc="..."]')
n, d = need_app(toks[0], True)
an, method, path = toks[1].lower(), toks[2].upper(), toks[3]
if method not in METHODS:
    fail("The method must be one of " + ", ".join(sorted(METHODS)))
opts, cur = {}, None
for t in toks[4:]:                      # an option's value runs until the next key=, so quotes are optional
    k, eq, v = t.partition("=")
    if eq and k in {"params", "format", "list", "body", "desc"}:
        cur = k
        opts[k] = v
    elif cur:
        opts[cur] += " " + t
    else:
        fail(f"I do not know '{t}'. Options: params=, format=, list=, body=, desc=")
for k, v in list(opts.items()):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        opts[k] = v[1:-1]
params = {}
for spec in [p for p in opts.get("params", "").split(",") if p]:
    pn, _, kind = spec.partition(":")
    params[pn] = {"int": {"pat": r"\d{1,12}"}, "word": {"pat": r"[A-Za-z0-9_.\-]{1,100}"}, "text": {"pat": r"[\s\S]{1,4000}"}, "": {"pat": r"[^\x00-\x1f\x7f]{1,2000}"}}.get(kind)
    if params[pn] is None:
        fail(f"Parameter type '{kind}' is not known. Use int, word or text.")
a = {"method": method, "path": path}
if params:
    a["params"] = params
for k in ("format", "list", "desc"):
    if k in opts:
        a[k] = opts[k]
if "body" in opts:
    try:
        a["body"] = json.loads(opts["body"])
    except ValueError:
        fail("body= must be valid JSON, for example body='{\"text\":\"{text}\"}'")
nd = {**d, "actions": {**d["actions"], an: a}}
why = check_def(n, nd)
if why:
    fail(why)
u = user_defs()
u[n] = nd
save("adapters.json", u)
print(f"Saved {n} {an} ({'WRITE: it will ask first' if is_write(a) else 'read'}).   Use it:  app {'do' if is_write(a) else 'read'} {n} {an}" + ("".join(f" {p}=..." for p in params)))
