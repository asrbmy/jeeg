# keywords: realtest, real pc test
# desc: Test JeeG on this real computer, by yourself or with an AI you connected (Claude.ai...). Harmless checks only; makes a private report you can share. real test list | run <group> | report | ai | manual
# category: selfcheck
# network: yes
# usage: real test list | real test run <group|id|all> | real test show <id> | real test compare | real test report | real test ai | real test manual | real test clear
# rawargs: full
# patterns: ^\s*real[\s\-]*(?:world\s+)?test\b ;; \btest\s+jeeg\s+on\s+(?:my\s+|this\s+)?(?:real\s+)?(?:pc|computer|laptop|machine)\b
# priority: 5
import json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(here))
import jeeg
from _lib import args_text, data_dir, fail, notify, output_dir
import _realtest as RT

text = re.sub(r"^\s*real[\s\-]*(?:world\s+)?test\s*", "", args_text(), flags=re.I).strip().lower()
text = re.sub(r"^\s*test\s+jeeg\s+on\s+(?:my\s+|this\s+)?(?:real\s+)?(?:pc|computer|laptop|machine)\s*", "", text) if text.startswith("test jeeg") else text
store = data_dir() / "realtest.json"


def load():
    try:
        d = json.loads(store.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save(d):
    store.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


hstore = data_dir() / "realtest_history.json"


def hist():
    try:
        d = json.loads(hstore.read_text(encoding="utf-8"))
        return d if isinstance(d, list) else []
    except (OSError, ValueError):
        return []


def snapshot(res):
    """After each run: remember every result (status only) with the JeeG version, so two runs can be compared."""
    h = hist()
    h.append({"ts": int(time.time()), "version": jeeg.__version__, "status": {k: v.get("status", "?") for k, v in res.items()}})
    hstore.write_text(json.dumps(h[-10:], indent=1), encoding="utf-8")


def update_note():
    h = hist()
    if h and h[-1].get("version") != jeeg.__version__:
        return f"JeeG was updated ({h[-1].get('version')} -> {jeeg.__version__}) since your last real test. Run it again:  real test run all     then:  real test compare"
    return ""


def compare():
    h = hist()
    if len(h) < 2:
        fail("Compare needs two runs. Run  real test run all  now, and again later (for example after updating JeeG).")
    a, b = h[-2], h[-1]
    when = lambda x: time.strftime("%Y-%m-%d %H:%M", time.localtime(x["ts"]))
    print(f"Before: {when(a)}  JeeG {a.get('version')}\nAfter:  {when(b)}  JeeG {b.get('version')}" + ("   (updated in between)" if a.get("version") != b.get("version") else ""))
    rank = {"pass": 0, "manual": 0, "skip": 1, "warn": 1, "fail": 2}
    worse, better, new, gone = [], [], [], []
    for k in sorted(set(a["status"]) | set(b["status"])):
        x, y = a["status"].get(k), b["status"].get(k)
        if x is None:
            new.append(f"{k} ({y})")
        elif y is None:
            gone.append(k)
        elif x != y:
            (worse if rank.get(y, 1) > rank.get(x, 1) else better).append(f"{k}: {x} -> {y}")
    for title, items in (("Got worse", worse), ("Got better", better), ("New checks", new), ("Checks no longer there", gone)):
        if items:
            print(f"\n{title} ({len(items)}):\n  " + "\n  ".join(items))
    if not (worse or better or new or gone):
        print("\nNo differences: every check has the same result.")
    elif worse:
        print("\nSend the 'Got worse' lines (with  real test report ) to whoever fixes JeeG.")


def show_list():
    res = load()
    if update_note():
        print(update_note() + "\n")
    print(f"Real-PC test: {len(RT.STEPS)} harmless checks in {len(RT.GROUPS)} groups (look-only or preview; nothing is installed, changed or sent).")
    for g in RT.GROUPS:
        steps = [s for s in RT.STEPS if s["group"] == g]
        done = sum(1 for s in steps if s["id"] in res)
        print(f"\n{g}  ({done}/{len(steps)} run) - {RT.GROUP_HELP[g]}")
        for s in steps:
            r = res.get(s["id"])
            print(f"  {s['id']:<18} {s['title']}" + (f"   [{r['status']}]" if r else ""))
    print("\nRun a group:  real test run system        everything:  real test run all        then:  real test report")


def sandbox_dir():
    d = Path(tempfile.mkdtemp(prefix="jeeg-realtest-"))
    (d / "hello.txt").write_text("hello world\n", encoding="utf-8")
    (d / "notes.txt").write_text("some notes\nsecond line\n", encoding="utf-8")
    (d / "sub").mkdir()
    (d / "sub" / "deep.txt").write_text("deep\n", encoding="utf-8")
    return d


def builtin(step):
    """Checks that look at this computer directly. -> (status, detail, out)"""
    if step["builtin"] == "tunnel":
        found = [n for n in ("cloudflared", "ngrok", "ssh") if shutil.which(n)]
        if found:
            return "pass", "found: " + ", ".join(found), ""
        return "warn", "no cloudflared, ngrok or ssh found", ""
    if step["builtin"] == "notify":
        shown = notify("JeeG real test", "If you can read this, notifications work.")
        return ("manual", step["ask"], "") if shown else ("warn", "this computer has no notification tool JeeG can use (Linux needs notify-send)", "")
    return "fail", "unknown built-in check", ""


def app_steps():
    """One step per linked app: reads only report whether they worked; write actions are shown as a preview and never sent."""
    import _adapters as A
    out = []
    for name, (d, _) in sorted(A.all_adapters().items()):
        has_login = d["auth"] == "none" or bool(A.get_secret(name, d))
        reads = [an for an, a in sorted(d["actions"].items()) if not A.is_write(a) and not (a.get("params") or {})]
        writes = [(an, a) for an, a in sorted(d["actions"].items()) if A.is_write(a)]
        if reads:
            out.append({"id": f"apps.{name}.read", "group": "apps", "title": f"{d.get('title', name)}: read", "q": f"app read {name} {reads[0]}", "login": has_login, "login_name": name,
                        "expect": "", "quiet": True, "kind": "soft"})
        if writes:
            an, a = writes[0]
            sample = {"github": "repo=o/r number=1 text=test", "telegram": "chat=1 text=test", "discord": "text=test", "slack": "text=test", "whatsapp": "phone=15555550100 text=test"}.get(name, "")
            if sample or not (a.get("params") or {}):
                out.append({"id": f"apps.{name}.write", "group": "apps", "title": f"{d.get('title', name)}: write (preview only)", "q": f"app do {name} {an} {sample} preview", "login": has_login,
                            "login_name": name, "expect": "Preview only", "quiet": False})
    return out


def run_steps(steps, budget):
    res = load()
    sb = None
    t0 = time.time()
    ran = 0
    for s in steps:
        if time.time() - t0 > budget:
            left = len(steps) - ran
            print(f"\n(stopped after {int(time.time() - t0)}s to stay inside the time limit; {left} check(s) left. Run the same line again to continue.)")
            break
        ran += 1
        if s.get("builtin"):
            status, detail, out = builtin(s)
            ms = 0
        elif s.get("login") is False:
            status, detail, out, ms = "skip", f"not logged in. To include it: app login {s['login_name']}", "", 0
        else:
            q = s["q"]
            cwd = None
            if s.get("cwd") == "sandbox" or "{sandbox}" in q:
                sb = sb or sandbox_dir()
                cwd = str(sb)
                q = q.replace("{sandbox}", str(sb))
            t = time.time()
            try:
                r = subprocess.run(list(jeeg.SELF_CMD) + q.split(), capture_output=True, text=True, timeout=s.get("timeout", 20), cwd=cwd,
                                   stdin=subprocess.DEVNULL, encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
                rc, out = r.returncode, r.stdout + r.stderr
            except subprocess.TimeoutExpired:
                rc, out = 124, "timed out"
            except OSError as ex:
                rc, out = 127, str(ex)
            ms = int((time.time() - t) * 1000)
            status, detail = RT.judge(s, rc, out, ms)
            if s.get("quiet"):
                out = ""
                detail = "worked" if status == "pass" else detail.split(":")[0] if rc else detail
                if status == "pass":
                    detail = "worked (the app's content is never shown here)"
        tag = {"pass": "PASS", "warn": "warn", "fail": "FAIL", "skip": "skip", "manual": "MANUAL"}[status]
        print(f"  {tag:<6} {s['id']:<18} {s['title']}" + (f"   ({RT.redact(detail)})" if detail and status != "pass" else ""), flush=True)
        res[s["id"]] = {"status": status, "ms": ms, "detail": detail, "out": (out or "")[:800] if status in {"fail", "warn"} else "", "ts": int(time.time()),
                  "title": s["title"], "q": s.get("q", "")}
        save(res)
    if sb:
        shutil.rmtree(sb, ignore_errors=True)
    return res


def all_steps():
    return RT.STEPS[:-1] + app_steps() + RT.STEPS[-1:]


def pick(spec):
    steps = all_steps()
    spec = spec.strip().lower()
    if spec in {"all", "everything"}:
        return steps
    if spec in RT.GROUPS:
        return [s for s in steps if s["group"] == spec]
    return [s for s in steps if s["id"] == spec] or None


if not text or text in {"help", "?"}:
    print("Real-PC test: checks that JeeG works on THIS computer, harmless (look-only or preview).")
    print("  real test list            what will be checked")
    print("  real test run system      run one group (or: all, or one id like system.disk)")
    print("  real test compare         what changed since the run before (for example after an update)")
    print("  real test report          a private report you can share (names, addresses and secrets removed)")
    print("  real test ai              the text to paste into Claude.ai so it runs the test for you through JeeG")
    print("  real test manual          what only a person can check")
    raise SystemExit(0)
if text == "compare":
    compare()
    raise SystemExit(0)
if text == "list":
    show_list()
    raise SystemExit(0)
m = re.match(r"^run\s+([a-z0-9_.]+)$", text)
if m:
    steps = pick(m.group(1))
    if not steps:
        fail("Unknown group or step. Groups: " + ", ".join(RT.GROUPS) + ", all.  See:  real test list")
    interactive = sys.stdout.isatty() and sys.stdin is not None and sys.stdin.isatty()
    print(f"Running {len(steps)} check(s)...")
    budget = 600 if interactive else 45
    try:
        budget = min(budget, float(os.environ.get("JEEG_REALTEST_BUDGET", budget)))       # tests only: it can only make the run shorter
    except ValueError:
        pass
    note = update_note()
    res = run_steps(steps, budget)
    snapshot(res)
    bad = sum(1 for s in steps if res.get(s["id"], {}).get("status") == "fail")
    print(f"\n{len(steps)} check(s) in this run, {bad} failed.   Next:  real test report" + ("   or:  real test compare" if len(hist()) > 1 else ""))
    if note:
        print(note.split("  Run it again")[0])
    raise SystemExit(0)
m = re.match(r"^show\s+([a-z0-9_.]+)$", text)
if m:
    s = next((x for x in all_steps() if x["id"] == m.group(1)), None)
    r = load().get(m.group(1))
    if not s:
        fail("No such step. See:  real test list")
    print(f"{s['id']} - {s['title']}")
    if s.get("q"):
        print("command: " + RT.redact(s["q"].replace("{sandbox}", "<sandbox>")))
    if not r:
        print("not run yet.  real test run " + s["id"])
        raise SystemExit(0)
    print(f"result: {r['status']} ({r['ms']} ms)\n" + RT.redact(r.get("detail", "")))
    if r.get("out"):
        print("output:\n" + RT.redact(r["out"]))
    if RT.HINTS.get(s["id"]):
        print("hint: " + RT.HINTS[s["id"]])
    raise SystemExit(0)
if text == "report":
    res = load()
    if not res:
        fail("Nothing has been run yet.  real test run all")
    md = RT.report(res, jeeg.__version__, getattr(sys, "frozen", False))
    p = output_dir("JeeG reports") / f"real-test-{time.strftime('%Y%m%d-%H%M')}.md"
    p.write_text(md, encoding="utf-8")
    print(RT.report(res, jeeg.__version__, getattr(sys, "frozen", False), max_chars=9000))
    print(f"\nSaved to {RT.redact(str(p))}")
    print("This report has no names, IP addresses, e-mail addresses or secrets in it. Read it, then send it to whoever is fixing JeeG, or paste it to an AI.")
    raise SystemExit(0)
if text == "ai":
    print(RT.brief())
    print("\n---\nFirst connect the AI:  connect ai ask   (see REMOTE_AI.md), then paste everything above the line into Claude.ai.")
    raise SystemExit(0)
if text == "manual":
    print("Only a person can check these:")
    for i, mline in enumerate(RT.MANUAL, 1):
        print(f"{i}. {mline}")
    raise SystemExit(0)
if text == "clear":
    try:
        store.unlink()
    except OSError:
        pass
    print("Cleared the saved results.")
    raise SystemExit(0)
fail("Try:  real test list   |   real test run system   |   real test report   |   real test ai")
