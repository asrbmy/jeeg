# keywords: event rules, rule add, rules list, when something new, on new item, trigger a task, watch an app
# desc: Run a task when something new shows up in a linked app: rule add issues when github issues changes then say new issue {new}. Lists, removes and runs rules (rules run once | rules run). Terminal only.
# category: apps_setup
# usage: rule add <name> when <app> <read-action> [args] changes [every N minutes] then <task words> | rules list | rule remove <name> | rules run once | rules run
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*(?:event\s+)?rules?\s+(?:add|list|remove|delete|run|show)\b ;; ^\s*(?:event\s+)?rules\s*$
# priority: 5
import hashlib, json, os, re, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _adapters import all_adapters, build, get_secret, is_write, parse_args, render, scrub, send
from _lib import args_text, fail
from _store import load, save

t = args_text().strip()
m = re.match(r"^(?:event\s+)?rules?\s*(add|list|remove|delete|run|show)?\b\s*(.*)$", t, re.I | re.S)
cmd, rest = ((m.group(1) or "list").lower(), m.group(2).strip()) if m else ("list", "")
tty = (sys.stdin is not None and sys.stdin.isatty()) or os.environ.get("JEEG_TEST_TTY") == "1"
if cmd not in {"list", "show"} and not tty:
    fail("Rules start tasks by themselves, so you set them up and run them yourself, in a terminal window. A program or an AI cannot.")


def rules():
    d = load("rules.json", {})
    return d if isinstance(d, dict) else {}


def h(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def clean(s):                                       # an item's text may be written by a stranger: it must never become a second command
    s = re.sub(r"[^\w\s.,:!?()#/@+\-]", " ", s)
    s = re.sub(r"\b(?:and|then)\b", "-", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip()[:160]


def fetch(r):
    ads = all_adapters()
    if r["app"] not in ads or r["action"] not in ads[r["app"]][0]["actions"]:
        raise RuntimeError("the app or action is gone")
    d = ads[r["app"]][0]
    a = d["actions"][r["action"]]
    if is_write(a):
        raise RuntimeError("that action changes things; a rule only watches")
    vals, why = parse_args(a, r.get("args", ""))
    if why:
        raise RuntimeError(why)
    secret = get_secret(r["app"], d) if d["auth"] != "none" else ""
    if d["auth"] != "none" and not secret:
        raise RuntimeError(f"not logged in to {r['app']}")
    _, text = send(build(r["app"], d, r["action"], vals, secret), secret)
    return [x.strip() for x in render(a, text, secret).splitlines() if x.strip() and not x.startswith("... and ")]


def then_run(r, new):
    import jeeg
    words = r["then"].replace("{new}", clean(new[0])).replace("{count}", str(len(new)))
    try:
        p = subprocess.run(list(jeeg.SELF_CMD) + [words], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
    except (OSError, subprocess.SubprocessError) as ex:
        return f"could not run: {ex}"
    out = re.sub(r"\s+", " ", p.stdout.decode("utf-8", "replace")).strip()[:160]
    if p.returncode == 3:
        return "that task asks for confirmation, so a rule cannot run it (skipped)"
    return ("ok: " if p.returncode == 0 else f"failed ({p.returncode}): ") + out


def one(name, r, now):
    """Look once. The first look only remembers what is there; after that, every new line starts the task."""
    try:
        lines = fetch(r)
    except RuntimeError as ex:
        r["last"] = f"{time.strftime('%H:%M')}  could not look: {ex}"
        return r["last"]
    seen = set(r.get("seen", []))
    new = [x for x in lines if h(x) not in seen]
    r["seen"] = (r.get("seen", []) + [h(x) for x in lines if h(x) not in seen])[-500:]
    r["next"] = now + r["every"] * 60
    if not r.get("started"):
        r["started"] = True
        r["last"] = f"{time.strftime('%H:%M')}  remembered {len(lines)} item(s); I will act on new ones"
        return r["last"]
    if not new:
        r["last"] = f"{time.strftime('%H:%M')}  nothing new"
        return r["last"]
    res = then_run(r, new[:5])
    r["last"] = f"{time.strftime('%H:%M')}  {len(new)} new -> {res}"
    return r["last"]


db = rules()
if cmd in {"list", "show"}:
    if not db:
        print("No rules yet. Example:\n  rule add issues when github issues changes then say new issue {new}")
    for n, r in sorted(db.items()):
        print(f"{n}: when {r['app']} {r['action']} {r.get('args', '')}".rstrip() + f" changes (every {r['every']} min) then {r['then']}")
        if r.get("last"):
            print("   last: " + r["last"])
    raise SystemExit(0)
if cmd in {"remove", "delete"}:
    n = rest.lower()
    if n not in db:
        fail(f"No rule called '{n}'. See:  rules list")
    db.pop(n)
    save("rules.json", db)
    print(f"Removed rule {n}.")
    raise SystemExit(0)
if cmd == "add":
    mm = re.match(r"^([a-z][a-z0-9_\-]{1,23})\s+when\s+([a-z][a-z0-9_\-]*)\s+([a-z][a-z0-9_\-]*)\s*(.*?)\s+changes(?:\s+every\s+(\d{1,4})\s*(?:min\w*)?)?\s+then\s+(.+)$", rest, re.I | re.S)
    if not mm:
        fail("Say it like this:  rule add issues when github issues changes then say new issue {new}\n(optional: ... changes every 10 minutes then ...)")
    n, app, act, args, every, then = mm.group(1).lower(), mm.group(2).lower(), mm.group(3).lower(), mm.group(4).strip(), int(mm.group(5) or 5), mm.group(6).strip()
    if len(db) >= 20 and n not in db:
        fail("That is 20 rules already.")
    if len(then) > 200 or re.search(r"[\x00-\x1f]", then):
        fail("The task words are too long or have odd characters.")
    r = {"app": app, "action": act, "args": args, "every": max(1, min(1440, every)), "then": then}
    try:
        fetch(r)
    except RuntimeError as ex:
        fail(f"I could not look at that now, so the rule was not saved: {ex}")
    db[n] = r
    save("rules.json", db)
    print(f"Saved rule {n}. It remembers what is there on the first look, then acts on new items only.\nStart it:  rules run once    or keep it going:  rules run")
    raise SystemExit(0)
# run
once = rest.lower().startswith("once")
if not db:
    fail("No rules to run. Add one first:  rule add ...")
try:
    while True:
        now = time.time()
        for n, r in sorted(db.items()):
            if once or now >= r.get("next", 0):
                print(f"{n}: {one(n, r, now)}", flush=True)
        save("rules.json", db)
        if once:
            break
        time.sleep(5)
except KeyboardInterrupt:
    save("rules.json", db)
    print("Stopped.")
