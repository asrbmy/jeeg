"""v2.8 features: new tasks, chaining, typo fixing, piped input, autorun, habits."""
import json, os, re, stat, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
HOME = tempfile.mkdtemp(prefix="jeeg-v28-")
os.environ["JEEG_HOME"] = HOME
P = F = 0
def ok(c, label):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", label)

def jg(*words, input=None, env=None, cwd=None):
    e = dict(os.environ, JEEG_HOME=HOME); e.update(env or {})
    r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *words], input=input, capture_output=True, text=True, timeout=90, env=e, cwd=cwd, stdin=None if input is not None else subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr

def has(q, *needles, rc=0):
    code, out = jg(q)
    good = code == rc and all(n in out for n in needles)
    ok(good, f"{q!r} -> {out.strip()[:140]!r}")
    return out

# --- money (global)
has("salary breakup 5000 a month tax 20 pension 5", "Take-home", "3,750.00")
has("salary breakup 60000 a year tax 22", "3,900.00")
has("interest tax deposit 200000 rate 5 tax 25", "2,500.00", "7,500.00")
has("severance 5 years salary 4000 a month weeks 2", "9,230.77")
has("sip goal 1 million in 15 years at 8%", "2,889.85")
has("sip goal 50000 in 3 years at 0%", "1,388.89")
has("add card visa 15 nov 2026", "Saved visa"); has("cards", "visa")
has("gpa planner current 3.2 credits 90 target 3.4 next 30", "4.00")
has("gpa planner current 3.0 credits 60 target 3.2 next 60 scale 4", "3.40")
out = has("cite book Smith, John; Deep Learning; 2020; MIT Press", "Smith, J. (2020)", "Smith, John. Deep Learning. MIT Press, 2020.")
has("cite article Lee, Ann; Sleep; Journal of Rest; 2021; 12(3), 45-60", "Lee, A. (2021)")
has("salary breakup", "Usage", rc=1); has("sip goal", "Usage", rc=1); has("severance", "Usage", rc=1)
has("salary breakup 5000 tax 70 pension 40", "Check", rc=1)
# --- health, home, developer
has("medicine stock add metformin 30 2 a day", "15 days"); has("pills left", "metformin"); has("medicine refill metformin 20", "50 pills")
has("bp 135/85", "Saved BP"); has("bp 20/10", "Check", rc=1); has("sugar 105 fasting", "Saved sugar"); has("sugar 6.2 after meal", "mmol/L"); has("health summary", "Blood pressure")
has("fast start", "Fast started"); has("fast start", "already", rc=1); has("fast status", "Fasting for"); has("fast end", "Fast ended")
has("cylinder changed 20 oct", "Recorded"); has("cylinder changed 1 nov", "Recorded"); has("cylinder", "lasted about")
has("milk 1.5 at 60", "Logged milk"); has("maid absent 3 nov", "absent"); has("milk summary", "Total quantity")
has("flat members amit ravi sam", "Amit"); has("flat add rent 18000 paid by amit", "Added rent"); has("flat add tea 300 paid by zed", "Unknown", rc=1)
has("flat add groceries 900 paid by ravi split ravi sam", "Added"); has("flat summary", "Sam pays Amit", "Ravi pays Amit")
has("regex explain ^\\d{3}-\\w+$", "a digit, exactly 3 times", "end of the text"); has("regex explain (unclosed", "not a valid", rc=1)
has("color #ff8800", "rgb(255, 136, 0)"); has("color hsl 32 100 50", "#ff8800"); has("color rgb 300 0 0", "0 to 255", rc=1)
d = tempfile.mkdtemp(); Path(d, ".env").write_text("A=1\nB=\nZ=9\n"); Path(d, ".env.example").write_text("A=\nB=\nC=\n")
out = has(f"env check {d}", "Missing from .env: C", "Empty in .env: B", "not listed in .gitignore"); ok("=1" not in out and "9" not in out.replace("Missing", ""), "env check never prints values")
f = Path(d, "f.txt"); f.write_text("hi\n")
import hashlib; h = hashlib.sha256(b"hi\n").hexdigest()
has(f"verify checksum {f} {h}", "MATCH"); has(f"verify checksum {f} {'0' * 64}", "DIFFERENT", rc=1)
has("http headers localhost", "Usage", rc=1)

# --- optional PDF tasks: work when the libraries are there, explain themselves when not
try:
    import pypdf  # noqa
    have = True
except ImportError:
    have = False
pdfs = tempfile.mkdtemp()
if have:
    from pypdf import PdfWriter
    wr = PdfWriter()
    for _ in range(3): wr.add_blank_page(300, 400)
    with open(Path(pdfs, "t.pdf"), "wb") as fh: wr.write(fh)
    code, out = jg("rotate pdf t.pdf 90 pages 1-2", cwd=pdfs); ok(code == 0 and "Rotated pages 1-2" in out and Path(pdfs, "t-rotated.pdf").exists(), "rotate pdf " + out[:80])
    code, out = jg("rotate pdf t.pdf 45", cwd=pdfs); ok(code == 1 and "90, 180" in out, "rotate rejects 45")
    code, out = jg("watermark pdf t.pdf DRAFT", cwd=pdfs); ok(code == 0 and Path(pdfs, "t-watermarked.pdf").exists(), "watermark pdf " + out[:80])
    ok(len(pypdf.PdfReader(str(Path(pdfs, "t-watermarked.pdf"))).pages) == 3, "watermarked file is a valid 3-page PDF")
    code, out = jg("compress pdf t.pdf", cwd=pdfs); ok(code == 0, "compress pdf " + out[:80])
    try:
        import pypdfium2, PIL  # noqa
        code, out = jg("pdf to images t.pdf 72 dpi", cwd=pdfs); ok(code == 0 and len(list(Path(pdfs, "t-pages").glob("*.png"))) == 3, "pdf to images " + out[:80])
    except ImportError:
        code, out = jg("pdf to images t.pdf", cwd=pdfs); ok(code == 1 and "pip install" in out, "pdf to images explains the missing library")
else:
    for q in ("rotate pdf t.pdf 90", "compress pdf t.pdf", "watermark pdf t.pdf DRAFT", "pdf to images t.pdf"):
        code, out = jg(q, cwd=pdfs); ok(code == 1 and "pip install" in out or "Not found" in out, f"{q}: explains what to install")

# --- chaining
code, out = jg("gst 2500 18 then save it to a note"); ok(code == 0 and "Note saved" in out, "chain: note " + out[-80:])
notes = Path(HOME, "notes.txt").read_text(); ok("2,950.00" in notes and "|" in notes, "chain: the result was passed on")
code, out = jg("--dry-run", "gst 2500 18 then copy it"); ok(code == 0 and "then copy_to_clipboard" in out, "chain dry-run")
code, out = jg("qzxqzx then save it"); ok("Note saved" not in out, "chain: nothing runs when the first part is unknown")
code, out = jg("gst 2500 18 then write novel"); ok("novel" not in Path(HOME, "notes.txt").read_text(), "chain: only known sinks")
code, out = jg("shutdown pc then copy it"); ok("needs confirmation" in out or code == 3, "chain never runs confirm tasks " + out[:60])
code, out = jg("--json", "gst 2500 18 then save it to a note"); ok(json.loads(out)["exit"] == 0 and len(json.loads(out)["tasks"]) == 2, "chain in --json")

# --- typo fixing
sys.path.insert(0, str(ROOT))
import jeeg
ents = jeeg.active(jeeg.load_index(jeeg.script_dirs([])))
for typo, want in (("shutdwn pc", "shutdown pc"), ("wether report", "weather report"), ("calendr", None), ("gst amout 100 5", "gst amount 100 5"), ("opne youtub", "open youtube")):
    near = jeeg.did_you_mean(typo, ents)
    ok(bool(near) and (want is None or any(want in n or n in want for n in near)), f"typo {typo!r} -> {near}")
ok(jeeg.did_you_mean("zzzzqqqq xxxx", ents) == [], "no wild guesses for nonsense")

# --- piped input
code, out = jg("word", "count", input="one two three\nfour five\n"); ok("Words: 5" in out and "Lines: 2" in out, "pipe: word count " + out[:60])
code, out = jg("sort", "lines", input="b\na\nc\n"); ok(out.index("a") < out.index("c"), "pipe: sort lines")
code, out = jg("format", "json", input='{"a":1}'); ok('"a": 1' in out, "pipe: json")
code, out = jg("uppercase", input="quiet please"); ok("QUIET PLEASE" in out and "clipboard" not in out, "pipe: uppercase leaves the clipboard alone")
code, out = jg("word", "count", "alpha beta gamma", input="piped words ignored when you typed some"); ok("Words: 3" in out, "typed words win over a pipe")
code, out = jg("word", "count", input=""); ok(code != 0 or "Words: 0" in out or "Give" in out, "empty pipe handled")
code, out = jg("word", "count", input="x " * 400000); ok(code == 0 and "Words:" in out, "huge pipe is capped")

# --- autorun
sys.path.insert(0, str(ROOT)); import jeeg_autorun as A
ok(A.parse("morning at 9:00") == ("morning", 9, 0, A.DAYS), "autorun parse daily")
ok(A.parse("backup at 6:30 pm weekdays") == ("backup", 18, 30, A.DAYS[:5]), "autorun parse pm weekdays")
ok(A.parse("x y at 21:05 every sun,wed")[3] == ["wed", "sun"], "autorun parse days")
for bad in ("morning at 25:00", "morning", "update at 9:00", "x at 13 pm", "a" * 200 + " at 9:00"):
    try: A.parse(bad); ok(False, f"autorun rejects {bad[:20]!r}")
    except ValueError: ok(True, f"autorun rejects {bad[:20]!r}")
line = A.cron_line(ROOT, Path(HOME), "1", "gst 100 5%; rm -rf ~", 9, 5, A.DAYS[:5])
ok("rm -rf" in line and "'gst 100 5\\%; rm -rf ~'" in line and line.count("\n") == 0, "autorun quotes the phrase for cron")
ok(A.cron_line(ROOT, Path(HOME), "1", "x", 9, 0, A.DAYS).split()[:5] == ["0", "9", "*", "*", "*"], "cron daily")
ok(A.schtasks_args(ROOT, Path(HOME), "1", "x", 9, 0, A.DAYS[:2])[-3:] == ["/SC", "WEEKLY", "/D"] or "MON,TUE" in A.schtasks_args(ROOT, Path(HOME), "1", "x", 9, 0, A.DAYS[:2]), "schtasks weekly")
if os.name == "posix":
    fb = Path(tempfile.mkdtemp()); store = fb / "cron.txt"
    sh = fb / "crontab"; sh.write_text(f'#!/bin/sh\nF={store}\nif [ "$1" = "-l" ]; then [ -f $F ] && cat $F || exit 1; else cat > $F; fi\n'); sh.chmod(0o755)
    env = {"PATH": f"{fb}:{os.environ['PATH']}"}
    code, out = jg("autorun", "add", "show time", "at", "7:15", "am", "daily", env=env); ok(code == 0 and "Scheduled" in out and "jeeg-autorun:1" in store.read_text(), "autorun add " + out[:60])
    code, out = jg("autorun", "list", env=env); ok("show time" in out and "07:15" in out, "autorun list")
    code, out = jg("autorun", "remove", "1", env=env); ok(code == 0 and "jeeg-autorun" not in store.read_text(), "autorun remove")
    code, out = jg("autorun", "remove", "9", env=env); ok(code == 1, "autorun remove bad number")
    code, out = jg("--dry-run", "autorun", "add", "show time", "at", "9:00", env=env); ok("[dry-run]" in out and not Path(HOME, "autorun.json").read_text().count("show time"), "autorun dry-run changes nothing")

# --- plugin update
lib = {"JEEG_LIBRARY": str(ROOT / "library")}
code, out = jg("plugin", "get", "morse_code", "--yes", env=lib); ok(code == 0 and Path(HOME, "plugins", "morse_code.py").exists(), "plugin get " + out[:80])
code, out = jg("plugin", "outdated", env=lib); ok(code == 0 and "up to date" in out, "plugin outdated: nothing yet " + out[:80])
pf = Path(HOME, "plugins", "morse_code.py"); pf.write_text(pf.read_text() + "\n# my edit\n")
code, out = jg("plugin", "outdated", env=lib); ok("morse_code" in out and "different" in out, "plugin outdated lists the changed one")
code, out = jg("plugin", "update", "--yes", env=lib); ok(code == 0 and "Updated morse_code" in out and Path(HOME, "plugins", "morse_code.py.bak").exists() and "my edit" not in pf.read_text(), "plugin update " + out[:80])
code, out = jg("plugin", "update", env=lib); ok("up to date" in out, "plugin update: now current")
bad = Path(tempfile.mkdtemp()); (bad / "index.json").write_text((ROOT / "library" / "index.json").read_text()); (bad / "morse_code.py").write_text("print('tampered')\n")
pf.write_text(pf.read_text() + "\n# edit again\n")
code, out = jg("plugin", "update", "--yes", env={"JEEG_LIBRARY": str(bad)}); ok("NOT changed" in out and "tampered" not in pf.read_text(), "plugin update refuses a file that does not match its fingerprint " + out[:80])
for q, want in (("morse hello", ".... . .-.. .-.. ---"),):
    code, out = jg(q); ok(want in out, "installed plugin runs")

# --- habits
code, out = jg("my habits"); ok(code == 0 and "task runs" in out and "Most used" in out, "habits " + out[:80])
code, out = jg("my habits month"); ok("last 30 days" in out, "habits month")

print(f"v2.8 tests: {P} passed, {F} failed")
sys.exit(1 if F else 0)
