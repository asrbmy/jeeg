"""Tests for using JeeG as a library (import jeeg)."""
import os, sys, tempfile, threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["JEEG_HOME"] = tempfile.mkdtemp(prefix="jeeg-api-test-")
import jeeg

P = F = 0
def ok(cond, label):
    global P, F
    if cond: P += 1
    else: F += 1; print("FAIL:", label)

r = jeeg.run("gst 2500 18")
ok(r.ok and r.task == "gst_amount" and "2,950.00" in r.output and bool(r), "run by words")
ok(str(r) == r.output and r.lines and r.runs[0].exit == 0, "result basics")
ok(jeeg.gst_amount(1000, 18).ok, "task by attribute")
ok(jeeg.run_task("gst-amount", 1000, 18).output == jeeg.gst_amount(1000, 18).output, "run_task name forms")
ok("1,180.00" in jeeg.gst_amount(1000, 18).output, "gst values")
try: jeeg.run_task("no_such_task_zz"); ok(False, "unknown task")
except jeeg.UnknownTaskError as e: ok(isinstance(e, KeyError) and "no_such_task_zz" in str(e), "unknown task")
try: jeeg.not_a_task_zz; ok(False, "bad attr")
except AttributeError: ok(True, "bad attr")
try: jeeg._private; ok(False, "private attr")
except AttributeError: ok(True, "private attr")
ok("gst_amount" in dir(jeeg) and "run" in dir(jeeg), "dir lists tasks")

m = jeeg.find("open youtube", 3)
ok(m and m[0].name == "open_youtube" and len(m) <= 3, "find")
ok(jeeg.find("") == [], "find empty")
ts = jeeg.tasks()
ok(len(ts) >= 478 and jeeg.tasks(category="money") and all(t.category == "money" for t in jeeg.tasks(category="money")), "tasks")
ok(any(t.online for t in ts) and len(jeeg.tasks(online=True)) < len(ts) // 2, "online filter")
ok(sum(jeeg.categories().values()) == len(ts), "categories")
ok(jeeg.task_info("gst_amount").usage, "task_info")

bad = jeeg.run("qzxqzx")
ok(not bad.ok and bad.exit == 1 and not bad, "no match")
try: jeeg.run("qzxqzx", check=True); ok(False, "check")
except jeeg.JeeGError as e: ok(e.result.exit == 1, "check raises")
ok(jeeg.run("shutdown pc").needs_confirmation, "confirm tasks do not run")
ok(jeeg.run("web").exit == 1 and "terminal" in jeeg.run("web").output, "terminal-only")
ok(jeeg.run("").exit == 1, "empty")
for badq in (None, 5):
    try: jeeg.run(badq); ok(False, "type check")
    except TypeError: ok(True, "type check")
try: jeeg.run("x" * 5000); ok(False, "length")
except ValueError: ok(True, "length")
try: jeeg.run("gst 1 1", timeout=-1); ok(False, "timeout check")
except ValueError: ok(True, "timeout check")
ok(jeeg.run("gst 2500\x00 18\x07").ok, "control chars stripped")

# separate data folder, and no leakage into the default one
home = tempfile.mkdtemp(prefix="jeeg-api-home-")
j = jeeg.JeeG(home=home)
ok(j("add expense 250 food lunch").ok and (Path(home) / "expenses.csv").exists(), "own home")
ok("250" in j.show_expenses().output, "JeeG attribute task")
ok(not (Path(os.environ["JEEG_HOME"]) / "expenses.csv").exists(), "default home untouched")
ok(os.environ["JEEG_HOME"] != home and jeeg.STATE == Path(os.environ["JEEG_HOME"]), "state restored")
ok(not (Path(os.environ["JEEG_HOME"]) / "history.jsonl").exists(), "no history by default")
jeeg.run("gst 100 5", history=True)
ok((Path(os.environ["JEEG_HOME"]) / "history.jsonl").exists(), "history opt-in")
ok(j.find("gst")[0].name and j.tasks() and j.categories(), "JeeG methods")
try: j.nothing_here_zz; ok(False, "JeeG attr")
except AttributeError: ok(True, "JeeG attr")

# stdin cannot hang a call
ok(jeeg.run("gst 100 5").ok, "no prompt")

# threads
out = []
def work(i): out.append(jeeg.gst_amount(100 + i, 18).ok)
th = [threading.Thread(target=work, args=(i,)) for i in range(8)]
[t.start() for t in th]; [t.join() for t in th]
ok(len(out) == 8 and all(out), "threads")

rs = jeeg.run_many(["gst 100 5", "qzxqzx", "gst 200 5"])
ok([r.ok for r in rs] == [True, False, True], "run_many")
ok(len(jeeg.run_many(["gst 100 5", "qzxqzx", "gst 200 5"], stop_on_error=True)) == 2, "run_many stop")
try: jeeg.run_many("gst 1 1"); ok(False, "run_many str")
except TypeError: ok(True, "run_many str")
import asyncio
async def _go():
    a, b = await asyncio.gather(jeeg.arun("gst 100 5"), jeeg.JeeG().arun("gst 200 5"))
    return a.ok and b.ok
ok(asyncio.run(_go()), "arun")

seen = []
h1 = jeeg.on("before", lambda q: seen.append(("b", q)))
h2 = jeeg.on("after", lambda r: seen.append(("a", r.ok)))
jeeg.on("after", lambda r: 1 / 0)                    # a broken hook must not break the call
ok(jeeg.run("gst 100 5").ok and ("a", True) in seen and any(k == "b" for k, _ in seen), "hooks fire")
jeeg.off("before", h1); jeeg.off("after")
n = len(seen); jeeg.run("gst 100 5")
ok(len(seen) == n, "hooks removed")
try: jeeg.on("during", print); ok(False, "bad event")
except ValueError: ok(True, "bad event")
got = []
ok(jeeg.watch("gst 100 5", every=0.01, callback=got.append, times=3) == 3 and len(got) == 3, "watch times")
got2 = []
jeeg.watch("gst 100 5", every=0.01, callback=got2.append, times=3, only_changes=True)
ok(len(got2) == 1, "watch only_changes")
ev = threading.Event(); th = threading.Thread(target=jeeg.watch, args=("gst 100 5", 0.01), kwargs=dict(stop=ev)); th.start(); ev.set(); th.join(5)
ok(not th.is_alive(), "watch stop event")
try: jeeg.watch("x", every=0); ok(False, "watch every")
except ValueError: ok(True, "watch every")
import json, subprocess
lj = json.loads(subprocess.run([sys.executable, str(Path(__file__).resolve().parent.parent / "jeeg.py"), "--list-json"], capture_output=True, text=True).stdout)
ok(len(lj) == len(jeeg.tasks()) and {"name", "description", "category", "usage", "online", "confirm"} <= set(lj[0]), "--list-json")

print(f"api tests: {P} passed, {F} failed")
sys.exit(1 if F else 0)
