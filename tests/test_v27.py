"""Tests for version 2.7: --json/--output, first-run tour, misses export, new tasks, speed guard. Run: python tests/test_v27.py"""
import json, os, statistics, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fails, total = [], 0


def check(name, cond, info=""):
    global total
    total += 1
    if not cond:
        fails.append(name); print(f"FAIL  {name} {info}")


home = tempfile.mkdtemp()
jh = Path(home) / "jeeg"
env = dict(os.environ, HOME=home, USERPROFILE=home, JEEG_HOME=str(jh), PYTHONIOENCODING="utf-8", BROWSER="/bin/true")
work = Path(tempfile.mkdtemp())


def task(*a, cwd=None, e=None):
    return subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=e or env,
                          stdin=subprocess.DEVNULL, timeout=90, cwd=str(cwd or work))


# ------------------------------------------------------------ --json and --output
r = task("--json", "gst", "2500", "18")
try:
    j = json.loads(r.stdout)
except ValueError:
    j = {}
check("json is valid", j.get("exit") == 0 and j.get("tasks") and j["tasks"][0]["name"] == "gst_amount", r.stdout + r.stderr)
check("json carries the output", "2,950.00" in j.get("output", ""))
check("json has no '>>' header noise", ">>" not in j.get("output", "") and "ok in" not in j.get("output", ""))
j = json.loads(task("--json", "shutdown", "pc").stdout)
check("json never prompts; confirm tasks report exit 3", j["exit"] == 3 and "needs confirmation" in j["output"])
j = json.loads(task("--json", "qzxqzx", "wwvv").stdout)
check("json reports no match", j["exit"] == 1 and j["tasks"] == [])
j = json.loads(task("--json", "open", "gmail", "and", "open", "calendar").stdout)
check("json lists every task of a multi-task line", [t["name"] for t in j["tasks"]] == ["open_gmail", "open_calendar"], str(j))
check("json needs a task", task("--json").returncode == 1)
out = work / "o.txt"
r = task("--output", str(out), "gst", "1000", "18")
check("--output writes the file", r.returncode == 0 and "1,180.00" in out.read_text(), r.stdout + r.stderr)
check("--output file has no header noise", ">>" not in out.read_text())
r = task("--output", str(out), "gst", "1000", "18")
check("--output never overwrites", r.returncode == 1 and "already exists" in r.stdout)
check("--output refuses a folder", task("--output", str(work), "gst", "1", "1").returncode == 1)
check("--output refuses a missing folder", task("--output", str(work / "nope" / "x.txt"), "gst", "1", "1").returncode == 1)
out2 = work / "o2.json"
task("--json", "--output", str(out2), "gst", "100", "18")
check("--json and --output together", json.loads(out2.read_text())["tasks"][0]["name"] == "gst_amount")

# ------------------------------------------------------------ first-run tour (needs a terminal)
if os.name == "posix":
    import pty, select
    def talk(sends, tenv):
        pid, fd = pty.fork()
        if pid == 0:
            os.execve(sys.executable, [sys.executable, str(ROOT / "jeeg.py")], tenv)
        buf = b""
        def pump(t=3.0):
            nonlocal buf
            end = time.time() + t
            while time.time() < end:
                r, _, _ = select.select([fd], [], [], 0.2)
                if r:
                    try:
                        d = os.read(fd, 4096)
                    except OSError:
                        return
                    if not d:
                        return
                    buf += d
                    if b"[Y/n]" in buf or b"task>" in buf[-20:]:
                        return
        pump()
        for s in sends:
            os.write(fd, s.encode()); pump()
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.waitpid(pid, 0)
        except OSError:
            pass
        return buf.decode(errors="replace")
    t_home = tempfile.mkdtemp()
    tenv = dict(env, HOME=t_home, JEEG_HOME=str(Path(t_home) / "j"))
    out = talk(["n\n", "exit\n"], tenv)
    check("first run offers the tour", "First time here?" in out, out[-300:])
    check("declining the tour is remembered", (Path(t_home) / "j" / ".toured").exists())
    out = talk(["exit\n"], tenv)
    check("the tour is offered only once", "First time here?" not in out, out[-300:])

# ------------------------------------------------------------ misses export
task("zzqx", "vvbn")
r = task("misses", "export")
f = work / "jeeg-misses.txt"
check("misses export", r.returncode == 0 and f.is_file() and "zzqx vvbn" in f.read_text(), r.stdout)
check("misses export warns to review", "READ AND EDIT" in f.read_text())
check("misses export never overwrites", task("misses", "export").returncode == 1)
check("misses clear", task("misses", "clear").returncode == 0 and "Nothing missed" in task("misses").stdout)

# ------------------------------------------------------------ new tasks
r = task("add", "warranty", "laptop", "12", "mar", "2099")
check("warranty add", "Saved laptop" in r.stdout, r.stdout + r.stderr)
check("warranty list", "laptop" in task("warranties").stdout)
task("add", "warranty", "phone", "3", "jan", "2020")
check("warranty overdue flag", "OVERDUE" in task("warranties").stdout)
check("warranty remove", task("remove", "warranty", "phone").returncode == 0 and "phone" not in task("warranties").stdout)
check("warranty needs a date", task("add", "warranty", "laptop").returncode == 1)
check("vehicle dues", "insurance bike" in (task("add", "vehicle", "due", "insurance", "bike", "15", "dec", "2099").stdout + task("vehicle", "dues").stdout))
check("vaccines are private (not in history)", task("add", "vaccine", "asha", "polio", "12", "nov", "2099").returncode == 0 and "polio" not in (jh / "history.jsonl").read_text())
check("lend", "ravi owes you 500.00" in task("lend", "500", "to", "ravi", "for", "lunch").stdout)
check("borrow", "you owe asha 300.00" in task("borrow", "300", "from", "asha").stdout)
r = task("ledger").stdout
check("ledger shows both sides", "ravi" in r and "asha" in r and "500.00" in r and "300.00" in r, r)
check("part settle", "Still owed to you: 300.00" in task("settle", "ravi", "200").stdout)
check("full settle", "All settled" in task("settle", "ravi").stdout)
check("settle unknown", task("settle", "nobody").returncode == 1)
check("lend rejects nonsense", task("lend", "to", "ravi").returncode == 1)
check("lend rejects huge amounts", task("lend", "99999999999", "to", "ravi").returncode == 1)
check("ledger is private", "ravi" not in (jh / "history.jsonl").read_text())
check("weight log", "Logged 72.5 kg" in task("weight", "72.5", "kg").stdout)
check("weight lb converts", "Logged 68 kg" in task("weight", "150", "lb").stdout)
check("weight rejects nonsense", task("weight", "5", "kg").returncode == 1)
check("weight goal", "Goal set" in task("weight", "goal", "70").stdout)
check("reading list add", "Added: Atomic Habits" in task("add", "book", "Atomic", "Habits").stdout)
check("reading list duplicate", task("add", "book", "atomic", "habits").returncode == 1)
check("reading list finish", "Marked as finished" in task("finished", "book", "atomic", "habits").stdout)
(Path(home) / "Documents").mkdir(exist_ok=True)
r = task("what", "is", "due")
check("what is due includes the new dates", r.returncode == 0)
task("life", "report")
rep = list((Path(home) / "Documents" / "JeeG-reports").glob("*.html"))
check("life report includes weight", rep and "Weight" in rep[0].read_text())

# ------------------------------------------------------------ speed guard (generous: catches big regressions, not noise)
def median_time(args, n=5):
    ts = []
    for _ in range(n):
        t0 = time.perf_counter(); subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *args], capture_output=True, env=env, stdin=subprocess.DEVNULL); ts.append(time.perf_counter() - t0)
    return statistics.median(ts)
task("reindex")
v = median_time(["--version"])
check(f"--version starts fast ({v * 1000:.0f} ms)", v < 0.8)
g = median_time(["gst", "100", "18"])
check(f"a simple task finishes fast ({g * 1000:.0f} ms)", g < 1.8)

print(f"{total - len(fails)}/{total} v2.7 tests passed")
sys.exit(1 if fails else 0)
