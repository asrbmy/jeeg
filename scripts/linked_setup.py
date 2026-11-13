# keywords: app login, app logout, app add, app action, app remove, app preset, app keystore, app ai, link app, connect app, add my own app
# desc: Link JeeG to an app: log in (app login github), add your own app by its web address (app add trello https://api.trello.com/1 query:key), define what it can do (app action ...), log out or remove, use ready-made presets, keep logins in the system keychain, choose which apps an AI may use. Terminal only: an AI cannot do this.
# category: apps_setup
# usage: app login <app> [device client_id=...] | app preset list|add <name> [base=...] | app keystore on|off | app ai allow|deny <app> | app ai list|reset|dry on|off | app logout <app> | app add <name> <https://base> [none|bearer|basic|header:NAME|query:NAME] | app add <name> command | app action <app> <name> <GET|POST|...> </path> [params=a,b] [format="{x}"] [list=path] [body='{"k":"{a}"}'] [desc="..."] | app remove <name>
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*(?:app|linked)\s+(?:login|logout|add|action|remove|preset|keystore|ai)\b
# priority: 5
import json, os, re, sys
from _adapters import (AUTHS, METHODS, NAME, all_adapters, build, check_def, check_secret, drop_secret, get_secret, is_write, parse_args, render, send,
                       set_secret, user_defs)
from _conn import ask_secret, load_reg
from _adapters import KS
import _device, _keystore, _policy
from _presets import PRESETS
from _lib import args_text, fail
from _store import save

text = args_text().strip()
LOOK = re.match(r"^(?:app|linked)\s+(?:preset(?:\s+list)?|keystore(?:\s+status)?|ai(?:\s+list)?)\s*$", text, re.I) is not None      # only looking: fine for anyone
if not LOOK and not (sys.stdin is not None and sys.stdin.isatty()) and os.environ.get("JEEG_TEST_TTY") != "1":
    fail("Linking apps is done by you, in a terminal window, so a program or an AI cannot change it. Open a terminal and run the same words there.")
m = re.match(r"^(?:app|linked)\s+(login|logout|add|action|remove|preset|keystore|ai)\b\s*(.*)$", text, re.I | re.S)
if not m:
    fail("Try:  app login github     |   app preset list   |     app add <name> <https://base> [bearer]     |     app action <app> <name> GET /path")
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
    if len(toks) > 1 and toks[1].lower() == "device":
        kv = dict(t.split("=", 1) for t in toks[2:] if "=" in t)
        try:
            s = _device.login(n, kv.get("client_id", ""), kv.get("code_url", ""), kv.get("token_url", ""), kv.get("scope", ""))
        except RuntimeError as ex:
            fail(str(ex))
        why = check_secret(d, s)
        if why:
            fail(why)
        where = set_secret(n, d, s)
        print(f"Logged in to {n}. The login is kept {'in the system keychain' if where == 'keychain' else 'in a private file'}.")
        raise SystemExit(0)
    if d.get("login_help"):
        print(d["login_help"])
    s = ask_secret(f"Paste the {'webhook address' if d['auth'] == 'url' else 'token'} for {n} (nothing is shown; it stays on this computer): ")
    why = check_secret(d, s)
    if why:
        fail(why)
    where = set_secret(n, d, s)
    print(f"Saved your {n} login (" + ("in the system keychain" if where == "keychain" else "private to you, in a file only your user can read") + ").")
    act = d["actions"].get("me")
    if act and not is_write(act):
        try:
            _, out = send(build(n, d, "me", {}, s), s)
            print("Check: " + render(act, out, s))
        except RuntimeError as ex:
            print(f"Saved, but the check failed: {ex}")
    raise SystemExit(0)
if cmd == "keystore":
    sub = (toks[0].lower() if toks else "status")
    if sub == "status" or sub not in {"on", "off"}:
        print(f"Keychain storage: {'on' if _keystore.enabled() else 'off'}   (system: {_keystore.backend()}, {'tool found' if _keystore.available() else 'tool NOT found'})")
        raise SystemExit(0)
    if sub == "on":
        if not _keystore.available():
            fail("No keychain tool found here (Linux: install secret-tool / libsecret-tools; macOS: security is built in). Your logins stay in their private files.")
        _keystore.set_flag(True)
        moved, kept = 0, 0
        for n, (d, _b) in ads.items():
            if d["auth"] != "none" and not d.get("secret_from") and load_reg("appsecrets").get(n) != KS:
                v = get_secret(n, d)
                if v:
                    if set_secret(n, d, v) == "keychain":
                        moved += 1
                    else:
                        kept += 1
        print(f"Keychain storage is on. Moved {moved} login(s) into the keychain" + (f"; {kept} stayed in their file (could not be stored and read back)." if kept else ".") + " New logins go there too.")
        raise SystemExit(0)
    for n, (d, _b) in ads.items():                          # off: bring every login back into its file first
        if d["auth"] != "none" and not d.get("secret_from"):
            v = get_secret(n, d)
            _keystore.set_flag(False)
            if v:
                set_secret(n, d, v)
                _keystore.remove(n)
    _keystore.set_flag(False)
    print("Keychain storage is off. Your logins are back in their private files.")
    raise SystemExit(0)
if cmd == "ai":
    sub = (toks[0].lower() if toks else "list")
    p = _policy.get()
    names = [t.lower().strip(",") for t in toks[1:]]
    if sub in {"allow", "deny"}:
        bad = [x for x in names if x not in ads]
        if not names or bad:
            fail("Say which apps: app ai " + sub + " github telegram" + (f"   (not known: {', '.join(bad)})" if bad else ""))
        for x in names:
            if sub == "deny":
                p["ai_deny"] = sorted(set(p["ai_deny"]) | {x})
                p["ai_allow"] = [y for y in p["ai_allow"] if y != x]
            else:
                p["ai_allow"] = sorted(set(p["ai_allow"]) | {x})
                p["ai_deny"] = [y for y in p["ai_deny"] if y != x]
        _policy.put(p)
    elif sub == "dry":
        p["dry"] = bool(toks[1:] and toks[1].lower() in {"on", "yes", "true"})
        _policy.put(p)
    elif sub == "reset":
        _policy.put({"ai_allow": [], "ai_deny": [], "dry": False})
        p = _policy.get()
    elif sub != "list":
        fail("Try:  app ai allow github   |   app ai deny telegram   |   app ai dry on   |   app ai list   |   app ai reset")
    p = _policy.get()
    print("AI rules for linked apps:")
    print("  only these apps: " + (", ".join(p["ai_allow"]) or "(any app you logged in to)"))
    print("  never these:     " + (", ".join(p["ai_deny"]) or "(none)"))
    print("  previews only:   " + ("yes (an AI never sends or changes anything)" if p["dry"] else "no"))
    raise SystemExit(0)
if cmd == "preset":
    sub = (toks[0].lower() if toks else "list")
    if sub == "list" or sub not in {"add"}:
        print("Ready-made apps (written from each service's public documentation; not tried against the live services, so test with a read action first):")
        for k, v in sorted(PRESETS.items()):
            reads = sum(1 for a in v["actions"].values() if not is_write(a))
            kind = "runs a program here" if v.get("local") else "web"
            print(f"  {k:<14} {v['title']:<34} {kind:<20} {reads} read, {len(v['actions']) - reads} write" + (f"   needs base={v['needs_base']}" if v.get("needs_base") else ""))
        print("Add one:  app preset add <name>      (rename it with as=<name>)")
        raise SystemExit(0)
    kv = dict(t.split("=", 1) for t in toks[2:] if "=" in t)
    pn = (toks[1].lower() if len(toks) > 1 else "")
    if pn not in PRESETS:
        fail("Pick one of: " + ", ".join(sorted(PRESETS)))
    v = PRESETS[pn]
    n = kv.get("as", pn).lower()
    if n in ads:
        fail(f"There is already an app called {n}. Use as=<another name>.")
    d = {k: x for k, x in v.items() if k != "needs_base"}
    if v.get("needs_base"):
        if not kv.get("base"):
            fail(f"{pn} needs your own address, for example:  app preset add {pn} base={v['needs_base']}")
        d["base"] = kv["base"].rstrip("/")
    why = check_def(n, d)
    if why:
        fail(why)
    if len(user_defs()) >= 30:
        fail("That is 30 apps already.")
    u = user_defs()
    u[n] = d
    save("adapters.json", u)
    print(f"Added {n}.  " + (f"Log in:  app login {n}\n  " if d["auth"] != "none" else "") + (v.get("login_help", "") + "\n  " if v.get("login_help") else "") + f"See what it can do:  apps {n}")
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
        fail("Usage:  app add <name> <https://api.example.com/v1> [none|bearer|basic|header:NAME|query:NAME]     or     app add <name> command")
    n = toks[0].lower()
    if n in ads:
        fail(f"There is already an app called {n}.")
    if toks[1].lower() == "command":
        d = {"title": n, "base": "", "auth": "none", "local": True, "actions": {}}
        why = check_def(n, d)
        if why:
            fail(why)
        u = user_defs()
        u[n] = d
        save("adapters.json", u)
        print(f"Added {n} (runs a program on this computer). Say what it can run, for example:\n  app action {n} status RUN git -C {{dir}} status --short params=dir read=yes\nWithout read=yes the action counts as a WRITE and asks first.")
        raise SystemExit(0)
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
if method not in METHODS | {"RUN"}:
    fail("The method must be one of " + ", ".join(sorted(METHODS)) + ", or RUN for a program on this computer")
argv = []
OPTK = {"params", "format", "list", "body", "desc", "read"}
rest_toks = toks[4:]
if method == "RUN":
    argv = [path]
    while rest_toks and not (rest_toks[0].partition("=")[1] and rest_toks[0].partition("=")[0] in OPTK):
        argv.append(rest_toks.pop(0))
opts, cur = {}, None
for t in rest_toks:                      # an option's value runs until the next key=, so quotes are optional
    k, eq, v = t.partition("=")
    if eq and k in OPTK:
        cur = k
        opts[k] = v
    elif cur:
        opts[cur] += " " + t
    else:
        fail(f"I do not know '{t}'. Options: params=, format=, list=, body=, desc=, read=yes")
for k, v in list(opts.items()):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        opts[k] = v[1:-1]
params = {}
for spec in [p for p in opts.get("params", "").split(",") if p]:
    pn, _, kind = spec.partition(":")
    params[pn] = {"int": {"pat": r"\d{1,12}"}, "word": {"pat": r"[A-Za-z0-9_.\-]{1,100}"}, "text": {"pat": r"[\s\S]{1,4000}"}, "": {"pat": r"[^\x00-\x1f\x7f]{1,2000}"}}.get(kind)
    if params[pn] is None:
        fail(f"Parameter type '{kind}' is not known. Use int, word or text.")
a = {"kind": "command", "argv": argv} if method == "RUN" else {"method": method, "path": path}
if "read" in opts:
    a["read"] = opts["read"].lower() in {"yes", "true", "on", "1"}
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
if method == "RUN" and not d.get("local"):
    fail(f"{n} is a web app. Make a program app first:  app add <name> command")
nd = {**d, "actions": {**d["actions"], an: a}}
why = check_def(n, nd)
if why:
    fail(why)
u = user_defs()
u[n] = nd
save("adapters.json", u)
print(f"Saved {n} {an} ({'WRITE: it will ask first' if is_write(a) else 'read'}).   Use it:  app {'do' if is_write(a) else 'read'} {n} {an}" + ("".join(f" {p}=..." for p in params)))
