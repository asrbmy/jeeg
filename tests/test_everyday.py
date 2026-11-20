"""New everyday tasks: documents, recurring costs, tracking, bank import, .ics, mileage, 80C, meals. Run: python tests/test_everyday.py"""
import csv, os, subprocess, sys, tempfile, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
HOME = tempfile.mkdtemp(prefix="jeeg-ev-"); os.environ["JEEG_HOME"] = HOME; os.environ["HOME"] = HOME; os.environ["USERPROFILE"] = HOME
P = F = 0
def j(q):
    r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), q], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
c, o = j("add document passport 12 mar 2031"); ok(c == 0 and "Saved passport" in o, "doc add " + o)
c, o = j("documents"); ok("passport" in o, "doc list")
c, o = j("remove document passport"); ok("Removed" in o, "doc remove")
c, o = j("recurring add 649 netflix entertainment"); ok(c == 0 and "649" in o, "rec add")
c, o = j("recurring apply"); ok("Added 1" in o, "rec apply " + o)
c, o = j("recurring apply"); ok("already added" in o, "rec twice")
rows = list(csv.DictReader(open(Path(HOME) / "expenses.csv"))) if (Path(HOME) / "expenses.csv").exists() else []
ok(len(rows) == 1 and rows[0]["category"] == "entertainment", "expense written once: %r" % rows)
c, o = j("recurring remove netflix"); ok("Removed" in o, "rec remove")
c, o = j("track stop"); ok(c != 0, "stop with nothing")
c, o = j("track start coding"); ok(c == 0, "track start")
c, o = j("track status"); ok("coding" in o, "track status")
c, o = j("track stop"); ok("Stopped coding" in o, "track stop")
c, o = j("track report"); ok("coding" in o, "track report")
b = Path(HOME) / "b.csv"
b.write_text("Date,Narration,Debit Amount,Credit Amount\n01/11/2026,SWIGGY,350.00,\n02/11/2026,SALARY,,5000\n")
c, o = j(f"import bank {b}"); ok("Imported 1" in o, "bank " + o)
c, o = j(f"import bank {b}"); ok("skipped 1" in o, "bank dup " + o)
(Path(HOME) / "a.csv").write_text("Date;Description;Amount;Type\n01-11-26;UPI-ZOMATO-1;250.00;DR\n02-11-26;SALARY;9000;CR\n")
c, o = j(f"import bank {Path(HOME) / 'a.csv'}"); ok("Imported 1" in o, "semicolon + 2-digit year + Dr/Cr " + o)
(Path(HOME) / "t.csv").write_text("Txn Date\tParticulars\tWithdrawal Amt.\tDeposit Amt.\tClosing Balance\n03/11/2026\tIRCTC\t800\t\t5000\n")
c, o = j(f"import bank {Path(HOME) / 't.csv'}"); ok("Imported 1" in o, "tab file " + o)
(Path(HOME) / "m.csv").write_text("Date,Details,Amount\n05 Nov 2026,Metro card,-120\n06 Nov 2026,Refund,300\n")
c, o = j(f"import bank {Path(HOME) / 'm.csv'}"); ok("Imported 1" in o and "120.00" in o, "minus = spending " + o)
c, o = j("import bank /nonexistent.csv"); ok(c != 0, "bank missing file")
c, o = j("calendar file dentist 25 dec 4pm for 30"); ics = list(Path(HOME).rglob("dentist-*.ics"))
ok(c == 0 and ics and "DTSTART:20261225T160000" in ics[0].read_text() and "DTEND:20261225T163000" in ics[0].read_text(), "ics " + o)
c, o = j("calendar file x"); ok(c != 0, "ics needs a date")
c, o = j("mileage add 25 km office"); ok(c == 0, "mileage add")
c, o = j("mileage rate 8"); c, o = j("mileage report"); ok("200.00" in o, "mileage claim " + o)
c, o = j("80c add 50000 ppf"); ok("1,00,000.00 still" in o, "80c " + o)
c, o = j("80c remove ppf"); c, o = j("80c"); ok(c != 0, "80c empty")
c, o = j("meal plan monday dal rice"); ok("Monday: dal rice" in o, "meal " + o)
c, o = j("meal plan funday x"); ok(c != 0, "bad day")
c, o = j("meal clear"); ok("cleared" in o, "meal clear")
sys.path.insert(0, str(ROOT))
import jeeg_autorun as A
ok(A.parse("show reminders at login") == ("show reminders", -1, -1, ["login"]), "autorun login parse")
ok(A.parse("x on startup")[3] == ["login"], "autorun startup parse")
ok(A.cron_line(ROOT, Path(HOME), "1", "x", -1, -1, ["login"]).startswith("@reboot"), "cron @reboot")
ok("ONLOGON" in A.schtasks_args(ROOT, Path(HOME), "1", "x", -1, -1, ["login"]), "schtasks ONLOGON")
ok(A.parse("x at 9:00 weekdays")[1] == 9, "timed autorun still parses")
shutil.rmtree(HOME, ignore_errors=True)
print(f"{P} passed, {F} failed"); sys.exit(1 if F else 0)
