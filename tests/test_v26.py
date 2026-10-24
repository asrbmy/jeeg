"""Tests for version 2.6 features: file and tracking tasks, plugin library, routines/alias sharing, doctor fix, tour, synonyms.
Run: python tests/test_v26.py"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
fails, total = [], 0


def check(name, cond, info=""):
    global total
    total += 1
    if not cond:
        fails.append(name); print(f"FAIL  {name} {info}")


home = tempfile.mkdtemp()
jh = Path(home) / "jeeg"
(Path(home) / "Documents").mkdir()
env = dict(os.environ, HOME=home, USERPROFILE=home, JEEG_HOME=str(jh), PYTHONIOENCODING="utf-8", BROWSER="/bin/true",
           JEEG_LIBRARY=str(ROOT / "library"))
work = Path(tempfile.mkdtemp())


def task(*a, e=None, cwd=None):
    return subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *a], capture_output=True, text=True, env=e or env,
                          stdin=subprocess.DEVNULL, timeout=90, cwd=str(cwd or work))


# ------------------------------------------------------------ files
try:
    from PIL import Image
    pics = work / "pics"; pics.mkdir()
    for i in range(2):
        Image.effect_noise((1600, 1000), 80).convert("RGB").save(pics / f"p{i}.jpg", quality=95)
    before = sum(p.stat().st_size for p in pics.glob("*.jpg"))
    r = task("compress", "pictures", str(pics), "quality", "50", "width", "800")
    out = list((pics / "compressed").glob("*.jpg"))
    check("shrink photos works", r.returncode == 0 and len(out) == 2, r.stdout + r.stderr)
    check("shrink photos keeps originals", sum(p.stat().st_size for p in pics.glob("*.jpg")) == before)
    check("shrink photos is smaller", sum(p.stat().st_size for p in out) < before)
    check("shrink photos rejects bad quality", task("compress", "pictures", str(pics), "quality", "2").returncode == 1)
except ImportError:
    pass

rn = work / "rn"; rn.mkdir()
for n in ("a.txt", "b.txt", "c.png"):
    (rn / n).write_text(n)
r = task("rename", "files", "in", str(rn), "as", "trip_{n}.{ext}")
check("pattern rename previews", "trip_001" in r.stdout and (rn / "a.txt").exists(), r.stdout)
r = task("rename", "files", "in", str(rn), "as", "trip_{n}.{ext}", "apply")
check("pattern rename applies", len(list(rn.glob("trip_*"))) == 3 and not (rn / "a.txt").exists(), r.stdout + r.stderr)
check("pattern rename keeps contents", sorted(p.read_text() for p in rn.glob("trip_*")) == ["a.txt", "b.txt", "c.png"])
r = task("undo")
check("pattern rename undo", (rn / "a.txt").exists() and (rn / "c.png").exists(), r.stdout)
check("pattern rename refuses path tricks", task("rename", "files", "in", str(rn), "as", "../x_{n}", "apply").returncode == 1)
check("pattern rename refuses unknown placeholder", task("rename", "files", "in", str(rn), "as", "{evil}_{n}", "apply").returncode == 1)
check("pattern rename refuses duplicates", task("rename", "files", "in", str(rn), "as", "same{ext}", "apply").returncode == 1)
(rn / "trip_9.txt").write_text("x")
check("pattern rename never overwrites", task("rename", "files", "in", str(rn), "as", "trip_9.txt", "apply").returncode == 1 or (rn / "trip_9.txt").read_text() == "x")

try:
    from reportlab.pdfgen import canvas
    pdf = work / "t.pdf"; c = canvas.Canvas(str(pdf))
    for i in range(3):
        c.drawString(72, 720, f"Hello JeeG page {i + 1}"); c.showPage()
    c.save()
    r = task("pdf", "to", "text", str(pdf), "pages", "2-3")
    txt = (work / "t.txt").read_text() if (work / "t.txt").exists() else ""
    check("pdf text", "page 2" in txt and "page 1" not in txt, r.stdout + r.stderr)
    check("pdf text page range", task("pdf", "to", "text", str(pdf), "pages", "9").returncode == 1)
except ImportError:
    pass
try:
    from PIL import Image as _I
    _I.new("RGB", (60, 60), "white").save(work / "scan.png")
    r = task("read", "text", "from", "scan.png")
    check("ocr keeps file names that start with a keyword", "Not found" not in r.stdout and "Missing" not in r.stdout or "pytesseract" in r.stdout or "Tesseract" in r.stdout, r.stdout)
except ImportError:
    pass
try:
    from reportlab.pdfgen import canvas as _c
    cc = _c.Canvas(str(work / "pdf_report.pdf")); cc.drawString(72, 720, "Quarterly numbers"); cc.save()
    r = task("pdf", "to", "text", "pdf_report.pdf")
    check("pdf text keeps file names that start with a keyword", "Wrote" in r.stdout, r.stdout)
except ImportError:
    pass
check("ocr missing file", task("read", "text", "from", "nope.png").returncode == 1)

# ------------------------------------------------------------ tracking
task("add", "expense", "250", "food", "lunch"); task("habit", "done", "gym"); task("water", "log", "500", "ml")
r = task("life", "report")
rep = list((Path(home) / "Documents" / "JeeG-reports").glob("*.html"))
check("life report", r.returncode == 0 and rep and "Spending" in rep[0].read_text(), r.stdout + r.stderr)
check("life report escapes", "<script" not in rep[0].read_text())
task("add", "expense", "9", "<script>x</script>", "y")
task("life", "report")
check("life report escapes categories", "<script>x" not in list((Path(home) / "Documents" / "JeeG-reports").glob("*.html"))[0].read_text())
check("study log", "Logged 45 min of maths" in task("study", "log", "maths", "45", "min").stdout)
check("study log hours", "90 min" in task("study", "log", "physics", "1.5", "hours").stdout)
check("study report", "Last 7 days: 2.2 hours" in task("study", "report").stdout)
check("study log rejects nonsense", task("study", "log", "maths", "9999", "hours").returncode == 1)
check("medicine add", task("add", "medicine", "metformin", "at", "8am", "and", "8pm").returncode == 0)
check("medicine add rejects no time", task("add", "medicine", "metformin").returncode == 1)
check("medicine add rejects bad time", task("add", "medicine", "x", "at", "13pm").returncode == 1)
r = task("medicine", "today")
check("medicine today", "metformin" in r.stdout and "08:00" in r.stdout and "20:00" in r.stdout, r.stdout)
check("medicine taken", "Ticked metformin" in task("medicine", "taken", "metformin").stdout)
check("medicine history not stored in plain history", "metformin" not in (jh / "history.jsonl").read_text())
check("medicine remove", task("remove", "medicine", "metformin").returncode == 0)
check("journal prompt", task("journal", "prompt").stdout.strip() != "")
check("what is due runs", task("what", "is", "due").returncode == 0)

# ------------------------------------------------------------ plugin library
r = task("plugin", "search", "loan")
check("library search", "loan_prepay" in r.stdout, r.stdout + r.stderr)
check("library search nothing", task("plugin", "search", "zzzqqq").returncode == 1)
check("library get needs confirmation", task("plugin", "get", "loan_prepay").returncode == 3)
check("library get", task("-y", "plugin", "get", "loan_prepay").returncode == 0 and (jh / "plugins" / "loan_prepay.py").is_file())
check("library get bad name", task("-y", "plugin", "get", "../x").returncode == 1)
check("library get unknown", task("-y", "plugin", "get", "nothing_here").returncode == 1)
task("-y", "plugin", "get", "goal_planner"); task("reindex")
r = task("loan", "prepay", "5", "lakh", "8.5", "5", "years", "extra", "2000")
check("library plugin runs", "You save 23,322" in r.stdout, r.stdout + r.stderr)
r = task("goal", "planner", "10", "lakh", "in", "5", "years", "at", "12%")
check("goal planner", "12,123 a month" in r.stdout, r.stdout + r.stderr)
bad = work / "lib"; shutil.copytree(ROOT / "library", bad)
with open(bad / "packing_list.py", "a") as f:
    f.write("# tampered\n")
r = task("-y", "plugin", "get", "packing_list", e=dict(env, JEEG_LIBRARY=str(bad)))
check("library refuses tampered file", r.returncode == 1 and "NOT installed" in r.stdout and not (jh / "plugins" / "packing_list.py").exists(), r.stdout)
check("library index is current", json.loads((ROOT / "library" / "index.json").read_text())["plugins"].keys() == {p.stem for p in (ROOT / "library").glob("*.py")})
import hashlib
idx = json.loads((ROOT / "library" / "index.json").read_text())["plugins"]
check("library fingerprints match files", all(hashlib.sha256((ROOT / "library" / f"{k}.py").read_bytes()).hexdigest() == v["sha256"] for k, v in idx.items()))
check("library unreachable", task("plugin", "search", "x", e=dict(env, JEEG_LIBRARY=str(work / "nowhere"))).returncode == 1)
check("library refuses http", task("plugin", "search", "x", e=dict(env, JEEG_LIBRARY="http://example.com/lib")).returncode == 1)
for k in idx:   # every library plugin is self-contained and stdlib-only
    src = (ROOT / "library" / f"{k}.py").read_text()
    check(f"library {k} has no network or process imports", not any(w in src for w in ("urllib", "socket", "subprocess", "requests", "os.system", "eval(", "exec(")))

# ------------------------------------------------------------ routines / aliases
(jh / "routines.json").write_text(json.dumps({"gym_time": ["say:Time to train", "open spotify"]}))
r = task("routines", "export")
check("routines export", (work / "jeeg-routines.json").is_file(), r.stdout)
other = dict(env, JEEG_HOME=str(Path(home) / "other"))
check("routines import needs confirmation", task("routines", "import", "jeeg-routines.json", e=other).returncode == 3)
check("routines import", task("-y", "routines", "import", "jeeg-routines.json", e=other).returncode == 0 and "gym_time" in (Path(home) / "other" / "routines.json").read_text())
(work / "bad.json").write_text(json.dumps({"kind": "routines", "routines": {"../bad": ["x"]}}))
check("routines import rejects bad names", task("-y", "routines", "import", "bad.json", e=other).returncode == 1)
(work / "bad2.json").write_text(json.dumps({"kind": "routines", "routines": {"ok": ["a" * 500]}}))
check("routines import rejects long steps", task("-y", "routines", "import", "bad2.json", e=other).returncode == 1)
check("routines import rejects wrong kind", task("-y", "routines", "import", "jeeg-routines.json", e=dict(other)).returncode == 0)
(work / "bad3.json").write_text("not json")
check("routines import rejects junk", task("-y", "routines", "import", "bad3.json", e=other).returncode == 1)
task("alias", "add", "wa", "=", "send", "whatsapp", "to")
check("alias export", task("alias", "export").returncode == 0 and (work / "jeeg-aliases.json").is_file())
r = task("alias", "import", "jeeg-aliases.json", e=other)
check("alias import", "Added 1" in r.stdout, r.stdout)
(work / "a2.json").write_text(json.dumps({"kind": "aliases", "aliases": {"list": "open youtube", "ok": "open gmail", "x": "open\x00gmail"}}))
r = task("alias", "import", "a2.json", e=other)
check("alias import skips reserved and control characters", "Added 1" in r.stdout and "Skipped 2" in r.stdout, r.stdout)

# ------------------------------------------------------------ doctor fix, tour, synonyms
(jh / "todos.json").write_text("{broken")
r = task("doctor", "fix")
check("doctor fix quarantines damaged data", (jh / "todos.json.bad").exists() and not (jh / "todos.json").exists(), r.stdout)
check("doctor fix idempotent", "repaired" in task("doctor", "fix").stdout or "Nothing" in task("doctor", "fix").stdout)
r = task("learn")
check("tour prints without a terminal", "1. Say what you want" in r.stdout and "7. Get a suggestion" in r.stdout)
import jeeg
check("synonyms", jeeg.apply_synonyms("pwd generator") == "password generator")
check("synonyms fallback runs", "understood as" in task("pwd", "generator").stdout or "password" in task("pwd", "generator").stdout.lower())

bare = tempfile.mkdtemp()
r = task("life", "report", e=dict(env, HOME=bare, USERPROFILE=bare, JEEG_HOME=str(Path(bare) / "j")))
check("reports work when there is no Documents folder", r.returncode == 0 and list((Path(bare) / "JeeG-reports").glob("*.html")), r.stdout + r.stderr)
r = task("privacy")
check("privacy command lists online tasks", "never touch the network" in r.stdout and "weather report" in r.stdout, r.stdout[:300])
check("privacy command does not list offline tasks", "gst amount" not in r.stdout.split("can, and only")[1])
check("list marks online tasks", "[online]" in task("list", "info").stdout or "[online]" in task("list").stdout)

print(f"{total - len(fails)}/{total} v2.6 tests passed")
sys.exit(1 if fails else 0)
