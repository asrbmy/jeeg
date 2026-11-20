"""More everyday tasks: summarize, download, meter, monthly report, budget alerts, kits, desktop input, windows. Run: python tests/test_more.py"""
import datetime, http.server, json, os, shutil, subprocess, sys, tempfile, threading
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
HOME = tempfile.mkdtemp(prefix="jeeg-mo-"); os.environ["JEEG_HOME"] = HOME; os.environ["HOME"] = HOME; os.environ["USERPROFILE"] = HOME
P = F = 0
def j(q, yes=False, env=None):
    r = subprocess.run([sys.executable, str(ROOT / "jeeg.py")] + (["--yes"] if yes else []) + [q], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL, env={**os.environ, **(env or {})})
    return r.returncode, r.stdout + r.stderr
def ok(c, l):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", l)
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        body = b"hello file" * 100
        if self.path == "/big": self.send_response(200); self.send_header("Content-Length", str(900 * 1024 * 1024)); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Length", str(len(body)))
        if self.path.startswith("/cd"): self.send_header("Content-Disposition", 'attachment; filename="../../evil.exe"')
        self.end_headers(); self.wfile.write(body)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H); PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
B = f"http://127.0.0.1:{PORT}"
# summarize
txt = Path(HOME) / "a.txt"
txt.write_text("Cats are small animals that sleep a lot during the day. Cats also hunt at night and cats are good at climbing trees.\n\nDogs are loyal animals that like to play outside. Many dogs enjoy long walks with their owners every morning.\n\nBirds can fly and sing in the early morning. Some birds migrate thousands of miles every year across oceans.\n\nFish live in water and breathe with gills. Cats sometimes try to catch fish from ponds.\n")
c, o = j(f"summarize {txt} 2"); ok(c == 0 and "Cats" in o and "not written by an AI" in o and o.count("  - ") == 2, "summarize " + o)
(Path(HOME) / "s.txt").write_text("Too short. Really.")
c, o = j(f"summarize {Path(HOME) / 's.txt'}"); ok(c != 0, "summarize short")
# clipboard (no clipboard tool in many test machines: must fail politely, not crash)
c, o = j("clipboard count"); ok("Traceback" not in o, "clipboard no crash")
# meter
c, o = j("meter add electricity 100"); ok(c == 0, "meter add")
m = json.loads((Path(HOME) / "meters.json").read_text()); m["electricity"][0]["d"] = (datetime.date.today() - datetime.timedelta(days=10)).isoformat()
(Path(HOME) / "meters.json").write_text(json.dumps(m))
c, o = j("meter add electricity 150"); c, o = j("meter use electricity"); ok("5.00 per day" in o, "meter use " + o)
c, o = j("meter add electricity 90"); ok(c != 0 and "lower" in o, "meter must not go down")
# download
c, o = j(f"download {B}/file.txt"); ok(c == 3, "download asks first rc=%s" % c)
c, o = j(f"download {B}/file.txt", yes=True); ok(c == 0 and (Path(HOME) / "Downloads" / "file.txt").stat().st_size == 1000, "download " + o)
c, o = j(f"download {B}/file.txt", yes=True); ok((Path(HOME) / "Downloads" / "file (1).txt").exists(), "never overwrites")
c, o = j(f"download {B}/cd", yes=True); ok(c != 0 and "will not download" in o and not list((Path(HOME) / "Downloads").glob("*evil*")), "bad name from header refused: " + o)
c, o = j(f"download {B}/x.exe", yes=True); ok(c != 0, "exe refused")
c, o = j(f"download {B}/big", yes=True); ok(c != 0 and "limit" in o, "too big refused " + o)
c, o = j("download file:///etc/passwd", yes=True); ok(c != 0, "file: refused")
c, o = j(f"download {B}/file.txt", yes=True, env={"JEEG_VIA_AI": "1"}); ok(c != 0, "an AI cannot download from this computer")
c, o = j(f"download {B}/file.txt preview"); ok(c == 0 and "Nothing was changed" in o, "download preview")
# monthly report + budget alert
c, o = j("monthly report"); ok(c != 0, "empty report refused")
j("add expense 500 food <b>x</b>"); j("set budget food 600"); j("recurring add 100 gym")
c, o = j("monthly report"); rp = list(Path(HOME).rglob("report-*.html"))
ok(c == 0 and rp and "&lt;b&gt;" not in rp[0].read_text() and "500.00" in rp[0].read_text() and "<script" not in rp[0].read_text(), "report " + o)
c, o = j("notify due"); ok("Budget food: 83% used" in o, "budget alert " + o)
# kits
j("alias add wa = open whatsapp"); j("set var rate = 18")
c, o = j("kit export mine"); kit = Path(HOME) / "JeeG kits" / "mine.jeegkit.json"; ok(c == 0 and kit.exists(), "kit export " + o)
c, o = j(f"kit show {kit}"); ok("1 alias" in o and "Nothing was changed" in o, "kit show")
bad = Path(HOME) / "bad.json"
bad.write_text(json.dumps({"kind": "kit", "routines": {"Good_one": ["open gmail"], "good_two": ["open\x07 gmail"], "../x": ["open gmail"], "fine": ["open gmail", "todo list"]}, "aliases": {"a" * 90: "open x"}, "vars": {"BAD NAME": 1}}))
c, o = j(f"kit show {bad}"); ok("routine fine" in o and "Ignored" in o, "bad parts ignored: " + o)
c, o = j(f"kit install {bad}"); ok(c == 3, "install asks first")
c, o = j(f"kit install {bad}", yes=True); cfg = json.loads((Path(HOME) / "routines.json").read_text()) if (Path(HOME) / "routines.json").exists() else {}
ok(c == 0 and "fine" in cfg and "good_two" not in cfg and "../x" not in cfg, "install only valid parts: %r" % list(cfg))
(Path(HOME) / "n.json").write_text('{"kind": "other"}'); c, o = j(f"kit show {Path(HOME) / 'n.json'}"); ok(c != 0, "not a kit")
# desktop + windows
c, o = j("desktop type hello preview"); ok(c == 0 and "Nothing was changed" in o, "desktop preview")
c, o = j("desktop click 5 6"); ok(c == 3, "desktop asks first")
c, o = j("desktop key"); ok(c != 0, "desktop key needs a key")
c, o = j("desktop type " + "x" * 400 + " preview"); ok(c != 0, "desktop text too long")
c, o = j("windows list"); ok("Traceback" not in o, "windows list no crash")
sys.path.insert(0, str(ROOT))
import jeeg_api, jeeg_remote
for w in ("desktop", "windows", "kit"):
    ok(w in jeeg_api.TERMINAL_ONLY and w in jeeg_remote.TERMINAL_ONLY, f"{w} is terminal-only for AI")
shutil.rmtree(HOME, ignore_errors=True)
print(f"{P} passed, {F} failed"); sys.exit(1 if F else 0)
