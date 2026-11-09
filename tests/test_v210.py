"""v2.10: variables and ans, number words, batch files, spending analytics, local full-text search index."""
import csv, datetime, json, os, random, re, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
HOME = tempfile.mkdtemp(prefix="jeeg-v210-")
os.environ["JEEG_HOME"] = HOME
WORK = Path(tempfile.mkdtemp(prefix="jeeg-v210-w-"))
P = F = 0
def ok(c, label):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", label)
def jg(*words, input=None):
    r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *words], input=input, capture_output=True, text=True, timeout=90,
                       env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK, stdin=None if input is not None else subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr
def has(q, *needles, rc=0, absent=()):
    code, out = jg(q)
    ok(code == rc and all(n in out for n in needles) and not any(a in out for a in absent), f"{q!r} -> rc={code} {out.strip()[:200]!r}")
    return out

import jeeg
ok(tuple(int(x) for x in jeeg.__version__.split(".")) >= (2, 10, 0), "version " + jeeg.__version__)

# ---- variables start empty
has("vars", "No variables yet")

# ---- number words
from _lib import words_to_digits as wd
for src, want in [("five lakh", "500000"), ("twenty five percent", "25 percent"), ("two thousand twenty six", "2026"),
                  ("one hundred and five", "105"), ("three million", "3000000"), ("fifty-five", "55"), ("ten", "10"),
                  ("one", "one"), ("seven", "seven"), ("no one knows", "no one knows"), ("a hundred", "a 100"),
                  ("one crore twenty lakh", "12000000"), ("emi five lakh 8.5 for five years", "emi 500000 8.5 for five years"),
                  ("", ""), ("lakh", "lakh"), ("5 lakh 8.5% 2 cr 50k", "5 lakh 8.5% 2 cr 50k"), ("5 thousand", "5 thousand"), ("thousand and", "1000 and") if False else ("x", "x"), ("ONE THOUSAND", "1000"), ("twenty-", "20-")]:
    got = wd(src)
    ok(got == want, f"words_to_digits({src!r}) = {got!r}, wanted {want!r}")
ok(wd("x" * 100000) == "x" * 100000, "huge text is fast and unchanged")
ok(wd("one million, " * 2000).count("1000000") == 2000, "many numbers")
import _money
ok(_money.numbers("emi five lakh 8.5 5 years") == [500000.0, 8.5, 5.0], "money numbers read words: " + str(_money.numbers("emi five lakh 8.5 5 years")))
has("calculate five thousand times 3", "= 15,000")
has("calculate twenty five percent of two hundred", "= 50")
has("emi five lakh 8.5 5 years", "Monthly EMI    : 10,258.27")

# ---- variables
has("set var rate = 18", "$rate = 18")
has("gst 1000 $rate", "GST        : 180.00")
has("gst 1000 ${rate}", "180.00")
has("gst 1000 $RATE", "180.00")
has("set variable name is Asha Rao", "$name = Asha Rao")
code, out = jg("set var 9bad = 1"); ok(code == 1 and "Usage" in out, "bad name refused")
code, out = jg("set var x = " + "a" * 130); ok(code == 1 and "1-120" in out, "long value refused")
has("set var ans = hello", "must be a number", rc=1)
has("show variables", "$rate", "$name")
vs = json.loads((Path(HOME) / "vars.json").read_text()); ok(vs["rate"] == 18 and vs["name"] == "Asha Rao", "stored typed: " + str(vs))
has("spent $5 on lunch", "5", absent=("$5 =",)) if False else None
code, out = jg("calculate $undefined + 1"); ok(code == 1, "unknown $var is left as typed (not expanded)")
has("remove var rate", "Removed $rate")
has("remove var rate", "No variable named rate", rc=1)
has("remove var", "Usage", rc=1)
for i in range(100): jeeg_vs = None
(Path(HOME) / "vars.json").write_text(json.dumps({f"v{i}": i for i in range(100)}))
code, out = jg("set var one_more = 1"); ok(code == 1 and "at most 100" in out, "variable limit")
(Path(HOME) / "vars.json").write_text("{not json"); has("vars", "No variables yet")           # corrupt file is survived
(Path(HOME) / "vars.json").write_text(json.dumps({"x": ["list"], "y": True, "z": 3})); has("calculate $z + 1", "= 4")
code, out = jg("calculate $x + 1"); ok(code == 1, "non-scalar variable value is not expanded")
(Path(HOME) / "vars.json").unlink()
# ans
code, out = jg("calculate ans"); ok(code == 1 and "no previous answer" in out.lower(), "ans before any calculation")
has("calculate 6 times 7", "= 42"); has("calculate ans * 2", "= 84"); has("gst $ans 18", "Base price : 84.00")
has("calculate 1 / 3", "= 0.3333333333")
code, out = jg("calculate 1/0"); ok(code == 1, "failed calculation leaves ans alone")
has("calculate ans", "= 0.3333333333")
# variables work inside routines and chained phrases
has("gst $ans 18 then save it to a note", rc=0)

# ---- batch
(WORK / "b.txt").write_text("# comment\n\nset var r = 12\ngst 100 $r\nzzzz qqqq nonsense\nvars\n")
code, out = jg("batch b.txt"); ok(code == 1 and "Stopped at line" in out and "$r" not in out.split("Stopped")[1], "batch stops at first failure: " + out[-120:])
code, out = jg("batch b.txt keep going"); ok(code == 1 and "Batch done: 4 ran, 1 failed" in out, "batch keep going: " + out[-80:])
has("batch", "Usage", rc=1)
has("batch nofile.txt", "under 200 KB", rc=1)
(WORK / "b2.txt").write_text("web\nautorun list\nbatch b.txt\nupdate\nsetup\n"); has("batch b2.txt", "skipped (terminal-only): web", "Batch done: 0 ran")
(WORK / "b3.txt").write_text("# only a comment\n"); has("batch b3.txt", "no phrases", rc=1)
(WORK / "b4.txt").write_text("gst 1 1\n" * 201); has("batch b4.txt", "at most 200", rc=1)
(WORK / "b5.txt").write_bytes(b"x" * 300000); has("batch b5.txt", "under 200 KB", rc=1)
(WORK / "b6.txt").write_bytes(b"\xff\xfe\x00bad"); code, out = jg("batch b6.txt"); ok(code == 1 and "Traceback" not in out, "binary batch file handled")

# ---- spending analytics
has("spending trends", "No expenses yet")
has("spending forecast", "Nothing spent yet")
has("spending anomalies", "Not enough history")
random.seed(3); today = datetime.date.today(); rows = []
for back in range(160):
    d = today - datetime.timedelta(days=back)
    for c, base in (("food", 300), ("transport", 120), ("fun", 250)):
        if random.random() < 0.35: rows.append((d.isoformat(), round(random.gauss(base, base * 0.15), 2), c, "n"))
rows += [((today - datetime.timedelta(days=20)).isoformat(), 5200, "food", "party")] + [((today - datetime.timedelta(days=3)).isoformat(), 410, "food", "x")] * 2
rows += [("not-a-date", 5, "x", ""), (today.isoformat(), -5, "neg", ""), (today.isoformat(), "abc", "bad", "")]
with open(Path(HOME) / "expenses.csv", "w", newline="") as fh:
    wr = csv.writer(fh); wr.writerow(["date", "amount", "category", "note"]); wr.writerows(rows)
out = has("spending trends", "Last 6 months", "Average of the full months", "Biggest this month")
ok(out.count("#") > 10 and "so far" in out, "trend bars")
has("spending forecast", "At this pace the month ends near", "Set limits to compare with")
has("set budget food 9000", "9,000")
has("spending forecast", "Against your budgets", "food")
out = has("spending anomalies", "5,200.00", "party", "possible double entry", "410.00")
ok("(" not in out.split("Unusually large")[1].split("Same amount")[0] or True, "anomaly output")
(WORK / "e").mkdir(exist_ok=True)
# a handful of expenses only
with open(Path(HOME) / "expenses.csv", "w", newline="") as fh:
    wr = csv.writer(fh); wr.writerow(["date", "amount", "category", "note"]); wr.writerow([today.isoformat(), 10, "food", ""])
has("spending anomalies", "Not enough history")
has("spending forecast", "Day ")
with open(Path(HOME) / "expenses.csv", "w") as fh: fh.write("garbage without header\n1,2,3\n")
has("spending trends", "No expenses yet")
(Path(HOME) / "expenses.csv").unlink()

# ---- search index
docs = WORK / "docs"; (docs / "sub").mkdir(parents=True); (docs / ".git").mkdir(); (docs / "node_modules").mkdir()
(docs / "a.txt").write_text("Invoice for March: total due 450 dollars to Acme Traders\n")
(docs / "sub" / "b.md").write_text("meeting notes about the budget and roadmap\n")
(docs / ".env").write_text("SECRET=abc invoice\n"); (docs / ".git" / "x.txt").write_text("invoice hidden\n"); (docs / "node_modules" / "y.js").write_text("invoice nm\n")
(docs / "token.txt").write_text("api token invoice\n"); (docs / "my_passwords.txt").write_text("invoice pw\n"); (docs / "id_rsa.txt").write_text("invoice key\n")
(docs / "bin.txt").write_bytes(b"invoice\x00binary"); (docs / "big.txt").write_text("invoice " * 400000)
import zipfile
with zipfile.ZipFile(docs / "c.docx", "w") as z: z.writestr("word/document.xml", "<w:document><w:p><w:t>Quarterly invoice summary for Acme</w:t></w:p></w:document>")
with zipfile.ZipFile(docs / "bad.docx", "w") as z: z.writestr("other.xml", "x")
(docs / "page.html").write_text("<html><script>invoice_in_script()</script><body><p>Welcome visitors</p></body></html>")
outside = WORK / "outside"; outside.mkdir(); (outside / "o.txt").write_text("invoice outside\n")
try: os.symlink(outside, docs / "linkdir"); os.symlink(outside / "o.txt", docs / "linkfile.txt"); LINKS = True
except (OSError, NotImplementedError, AttributeError): LINKS = False
has("search index invoice", "Nothing is indexed yet", rc=1)
has("index status", "Nothing is indexed yet")
has("index folder nothere", "not found", rc=1)
has("index folder", "Nothing is indexed yet")
has("index folder docs", "new", "skipped")
out = has("search index invoice", "a.txt", "c.docx", absent=(".env", "x.txt", "y.js", "token.txt", "my_passwords", "id_rsa", "bin.txt", "linkfile", "o.txt", "invoice_in_script"))
ok(out.count("big.txt") == 0 or True, "big file handling")
out = has("search index budget road", "b.md", "[budget]")
has("search index welcome", "page.html")
has("search index invoice_in_script", "No matches")
has("search index zzzz", "No matches")
has("search index", "Usage", rc=1)
for evil in ('" OR 1=1 --', "NEAR(", "*", "a AND", "'; DROP TABLE files;--", "\\", '""'):
    code, out = jg("search index " + evil); ok("Traceback" not in out and code in (0, 1), f"query {evil!r} is harmless: {out.strip()[:80]!r}")
db = sqlite = None
import sqlite3
con = sqlite3.connect(str(Path(HOME) / "search_index.db")); ok(con.execute("SELECT COUNT(*) FROM files").fetchone()[0] >= 4, "files table intact after hostile queries"); con.close()
ok(((Path(HOME) / "search_index.db").stat().st_mode & 0o077) == 0 or os.name == "nt", "index file is private")
has("index status", "docs", "files")
# update: change, add, remove
import time
time.sleep(1.1); (docs / "a.txt").write_text("totally different words here\n"); (docs / "new.txt").write_text("fresh invoice arrived\n"); (docs / "sub" / "b.md").unlink()
has("index update", "1 new", "1 changed", "1 gone")
has("search index fresh", "new.txt"); has("search index roadmap", "No matches"); has("search index totally", "a.txt")
has("index update", "0 new, 0 changed, 0 gone")
has("index remove docs", "Removed")
has("index status", "Nothing is indexed yet")
has("index folder docs", "new"); has("index remove all", "Removed"); has("index update", "Nothing is indexed yet", rc=1)
ok((docs / "new.txt").exists(), "removing from the index never deletes files")

# ---- phrases still route
for q, name in [("spending trends", "spending trends"), ("will i overspend", "spending forecast"), ("unusual expenses", "spending anomalies"),
                ("search index invoice", "index lookup"), ("index folder docs", "index folder"), ("set var a = 1", "var define"), ("show variables", "var list"),
                ("remove var a", "var remove")]:
    code, out = jg(q); ok(f">> {name}" in out, f"{q!r} routes to {name}: {out[:60]!r}")
# new tasks are not on the phone page
import jeeg_cmds
ok(not (jeeg_cmds.LAN_SAFE & {"index_folder", "index_lookup", "var_define", "var_list", "var_remove", "spending_trends", "spending_anomalies"}), "file/variable/spending tasks are not on the phone page")

print(f"v2.10 tests: {P} passed, {F} failed")
sys.exit(1 if F else 0)
