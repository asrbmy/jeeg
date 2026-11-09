"""v2.9 features: remembered picks, routine variables, report/share, standalone update, phone page,
extension origins, new tasks, send-to installer, browser extension files."""
import hashlib, http.server, json, os, re, shutil, socket, subprocess, sys, tempfile, threading, time, urllib.request, urllib.error
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
HOME = tempfile.mkdtemp(prefix="jeeg-v29-")
os.environ["JEEG_HOME"] = HOME
os.environ.pop("JEEG_API_TOKEN", None)
WORK = Path(tempfile.mkdtemp(prefix="jeeg-v29-work-"))
P = F = 0
def ok(c, label):
    global P, F
    if c: P += 1
    else: F += 1; print("FAIL:", label)

def jg(*words, input=None, cwd=None, env=None):
    e = dict(os.environ, JEEG_HOME=HOME); e.update(env or {})
    r = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), *words], input=input, capture_output=True, text=True, timeout=90, env=e,
                       cwd=cwd or WORK, stdin=None if input is not None else subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr

def has(q, *needles, rc=0, **kw):
    code, out = jg(q, **kw)
    ok(code == rc and all(n in out for n in needles), f"{q!r} -> rc={code} {out.strip()[:160]!r}")
    return out

import jeeg, jeeg_cmds, jeeg_bridge as B
ok(jeeg.__version__ >= "2.9.0", "version bumped " + jeeg.__version__)

# ---- remembered picks
entries = jeeg.active(jeeg.load_index(jeeg.script_dirs([])))
by = {e["name"]: e for e in entries}
jeeg._remember_pick("frequency count", by["word_frequency"], entries)
al = json.loads((Path(HOME) / "aliases.json").read_text())
ok(al.get("frequency count") == "word frequency", "pick remembered " + str(al))
jeeg._remember_pick("rate 5 things", by["word_frequency"], entries)
jeeg._remember_pick("a b c d e f", by["word_frequency"], entries)
jeeg._remember_pick("list", by["word_frequency"], entries)
al = json.loads((Path(HOME) / "aliases.json").read_text())
ok(set(al) == {"frequency count"}, "digits, long and reserved phrases are not remembered " + str(al))
# a pick whose name does not resolve back to itself is never stored
bad = dict(by["word_frequency"]); bad["name"] = "zzz_nothing"
jeeg._remember_pick("zzz pick", bad, entries)
ok("zzz pick" not in json.loads((Path(HOME) / "aliases.json").read_text()), "unresolvable pick not stored")

# ---- routine variables
import _routine
f = _routine.fill("report for {month} {year} on {weekday} ({today}) {1}", ["x"])
ok(re.search(r"report for [A-Z][a-z]+ 20\d\d on [A-Z][a-z]+day \(20\d\d-\d\d-\d\d\) x", f) is not None, "routine vars " + f)
ok(_routine.fill("{date} {week} {time}", []).count("{") == 0, "all date vars replaced")

# ---- undo hint
has("undo", "undo expense", rc=1)

# ---- report / share
home = str(Path.home())
has("report", "jeeg-report.txt")
rep = (WORK / "jeeg-report.txt").read_text()
ok("doctor" in rep and "JeeG " in rep and home not in rep.replace("~", ""), "report content")
ok("misses" not in rep.lower() or "Unmatched phrases saved" in rep, "report has no phrases")
has("share", "share plugin")
has("share aliases", "jeeg-aliases.json")
ok(json.loads((WORK / "jeeg-aliases.json").read_text())["kind"] == "aliases", "aliases shared")
(Path(HOME) / "plugins").mkdir(exist_ok=True)
(Path(HOME) / "plugins" / "demo_one.py").write_text("# keywords: demo one\n# desc: demo\nprint('hi')\n")
has("share plugin demo_one", "demo_one.py")
ok((WORK / "demo_one.py").exists(), "plugin file shared")
has("share plugin ../x", "Usage", rc=1)

# ---- standalone update (local fake release server, never the real GitHub)
NAME = jeeg_cmds.exe_asset_name()
BLOB = b"#!/bin/sh\necho new-version\n"
GOOD = hashlib.sha256(BLOB).hexdigest()
state = {"sha": GOOD}
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        base = f"http://127.0.0.1:{self.server.server_port}"
        if self.path == "/release":
            body = json.dumps({"tag_name": "v9.9.9", "html_url": base, "assets": [
                {"name": NAME, "browser_download_url": base + "/a"}, {"name": NAME + ".sha256", "browser_download_url": base + "/s"}]}).encode()
        elif self.path == "/release-nosha":
            body = json.dumps({"tag_name": "v9.9.9", "assets": [{"name": NAME, "browser_download_url": base + "/a"}]}).encode()
        elif self.path == "/a": body = BLOB
        elif self.path == "/s": body = (state["sha"] + "  " + NAME + "\n").encode()
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_port
os.environ["JEEG_RELEASE_API"] = f"http://127.0.0.1:{port}/release"
rel = jeeg_cmds.latest_release()
ok(rel["tag_name"] == "v9.9.9", "release read from override")
exe = WORK / "jeeg-fake"; exe.write_bytes(b"old")
ok(jeeg_cmds.update_standalone(rel, exe) == 0 and exe.read_bytes() == BLOB, "update replaces the program")
ok(not (WORK / "jeeg-fake.new").exists(), "no temp file left")
state["sha"] = "0" * 64
exe.write_bytes(b"old")
ok(jeeg_cmds.update_standalone(rel, exe) == 1 and exe.read_bytes() == b"old", "wrong SHA-256 is refused, program untouched")
state["sha"] = GOOD
os.environ["JEEG_RELEASE_API"] = f"http://127.0.0.1:{port}/release-nosha"
ok(jeeg_cmds.update_standalone(jeeg_cmds.latest_release(), exe) == 1 and exe.read_bytes() == b"old", "release without .sha256 is refused")
os.environ["JEEG_RELEASE_API"] = "http://evil.example/release"
ok(jeeg_cmds._release_api() == jeeg_cmds.RELEASE_API, "non-https, non-local override ignored")
os.environ["JEEG_RELEASE_API"] = "ftp://x"
ok(jeeg_cmds._release_api() == jeeg_cmds.RELEASE_API, "odd scheme ignored")
os.environ.pop("JEEG_RELEASE_API")
try:
    jeeg_cmds._download("http://evil.example/x", 10); ok(False, "http download refused")
except OSError:
    ok(True, "http download refused")
os.environ["JEEG_RELEASE_API"] = f"http://127.0.0.1:{port}/release"
try:
    jeeg_cmds._download(f"http://127.0.0.1:{port}/a", 5); ok(False, "size limit")
except OSError:
    ok(True, "download size limit")
ok(jeeg_cmds.install_kind(ROOT) in {"git", "zip", "pip"}, "install kind when not frozen")
code, out = jg("update", env={"JEEG_RELEASE_API": f"http://127.0.0.1:{port}/release"})
ok("newer version" in out and "9.9.9" in out, "update check against fake release " + out[:100])
srv.shutdown()

# ---- phone page (web lan)
s = socket.socket(); s.bind(("127.0.0.1", 0)); wp = s.getsockname()[1]; s.close()
proc = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "web", "lan", str(wp)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                        env=dict(os.environ, JEEG_HOME=HOME), cwd=WORK)
line = proc.stdout.readline()
m = re.search(r"http://([\d.]+):(\d+)/\?k=(\S+)", line)
ok(m is not None, "phone page prints a link " + line)
try:
    ip, k = m.group(1), m.group(3)
    base = f"http://{ip}:{wp}"
    def get(path, headers=None):
        try:
            with urllib.request.urlopen(urllib.request.Request(base + path, headers=headers or {}), timeout=10) as r: return r.status, r.read().decode()
        except urllib.error.HTTPError as e: return e.code, e.read().decode()
    ok(get("/")[0] == 403, "phone page needs the key")
    ok(get("/?k=wrong")[0] == 403, "wrong key refused")
    st, page = get(f"/?k={k}")
    ok(st == 200 and "JeeG" in page, "phone page opens with key")
    tok = re.search(r'const T="([^"]+)"', page).group(1)
    def run(q, host=None, origin=None):
        h = {"Content-Type": "application/json", "X-JeeG-Token": tok}
        if host: h["Host"] = host
        if origin: h["Origin"] = origin
        try:
            with urllib.request.urlopen(urllib.request.Request(base + "/run", json.dumps({"q": q}).encode(), h), timeout=30) as r: return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e: return e.code, {}
    st, j = run("gst 2500 18"); ok(st == 200 and "450.00" in j["out"], "phone page runs an everyday task")
    st, j = run("open youtube"); ok("not allowed" in j.get("out", ""), "phone page refuses app launching " + str(j))
    st, j = run("shutdown pc"); ok("not allowed" in j.get("out", ""), "phone page refuses shutdown")
    st, j = run("delete empty folders"); ok("not allowed" in j.get("out", ""), "phone page refuses file tasks")
    ok(run("gst 2500 18", host="evil.example")[0] == 403, "phone page host check")
    ok(run("gst 2500 18", origin="http://evil.example")[0] == 403, "phone page origin check")
    ok(get(f"/?k={k}", {"Host": "evil.example"})[0] == 403, "phone page GET host check")
    st, j = run("report"); ok("terminal" in j.get("out", ""), "report not available on the page")
    for q in ("open amazon", "open wikipedia", "hash text hello", "count words /etc/hostname", "json format /etc/hosts", "reading time /etc/hosts",
              "reverse text", "encode base64", "readability /etc/hostname", "type notes", "pomodoro", "gst 100 18 then copy it", "gst 100 18 then speak it",
              "run routine x", "clipboard history", "remind me in 1 minute to x then copy it", "organize downloads", "empty trash"):
        st, j = run(q)
        ok(any(x in j.get("out", "") for x in ("not allowed", "only available", "No single matching")) or st != 200, f"phone page refuses {q!r}: {j.get('out', '')[:70]!r}")
    # an alias that points at a blocked task is still blocked
    (Path(HOME) / "aliases.json").write_text(json.dumps({"harmless": "open amazon"}))
    st, j = run("harmless"); ok("not allowed" in j.get("out", ""), "alias to a blocked task is blocked: " + str(j)[:80])
    (Path(HOME) / "aliases.json").write_text(json.dumps({}))
    st, j = run("calculate 2+3*4"); ok("14" in j.get("out", ""), "allowed task works after")
    ok(all(isinstance(x, str) for x in jeeg_cmds.LAN_SAFE) and "open_amazon" not in jeeg_cmds.LAN_SAFE, "allow-list holds task names")
    names = {e["name"] for e in entries}
    ok(jeeg_cmds.LAN_SAFE <= names, "every allow-listed name is a real task: " + str(sorted(jeeg_cmds.LAN_SAFE - names)))
    risky = [e["name"] for e in entries if e["name"] in jeeg_cmds.LAN_SAFE and (e.get("confirm") or e.get("category") in {"files", "system", "apps", "power", "clipboard", "email"})]
    ok(not risky, "allow-list has no confirm/file/system tasks: " + str(risky))
finally:
    proc.terminate(); proc.wait(timeout=10)

# ---- downloads never follow a redirect to plain http
class R(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        self.send_response(302); self.send_header("Location", "http://evil.example/x"); self.end_headers()
rs = http.server.ThreadingHTTPServer(("127.0.0.1", 0), R); threading.Thread(target=rs.serve_forever, daemon=True).start()
try:
    jeeg_cmds._download(f"http://127.0.0.1:{rs.server_port}/a", 100); ok(False, "redirect to http refused")
except OSError:
    ok(True, "redirect to http refused")
os.environ["JEEG_RELEASE_API"] = f"http://127.0.0.1:{rs.server_port}/release"
try:
    jeeg_cmds.latest_release(); ok(False, "release check refuses http redirect")
except OSError:
    ok(True, "release check refuses http redirect")
rs.shutdown()

# ---- extension origins on the API
s = socket.socket(); s.bind(("127.0.0.1", 0)); ap = s.getsockname()[1]; s.close()
EXT = "chrome-extension://abcdefghijklmnopabcdefghijklmnop"
B.ALLOWED_ORIGINS.add(EXT)
tk = B.get_token()
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", ap), B.make_handler(tk, ap, B._cfg()))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
def call(method, path, headers=None, data=None):
    h = {"Authorization": "Bearer " + tk}; h.update(headers or {})
    req = urllib.request.Request(f"http://127.0.0.1:{ap}{path}", data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r: return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e: return e.code, dict(e.headers), e.read()
st, hd, body = call("GET", "/v1/health", {"Origin": EXT})
ok(st == 200 and hd.get("Access-Control-Allow-Origin") == EXT, "allowed extension origin works with CORS header")
ok(call("GET", "/v1/health", {"Origin": "http://evil.example"})[0] == 403, "web page origin still refused")
ok(call("GET", "/v1/health", {"Origin": "chrome-extension://zzzzzzzzzzzzzzzz"})[0] == 403, "other extension refused")
st, hd, _ = call("OPTIONS", "/v1/run", {"Origin": EXT, "Authorization": ""}); 
ok(st == 204 and "Authorization" in hd.get("Access-Control-Allow-Headers", ""), "preflight for the allowed extension")
ok(call("OPTIONS", "/v1/run", {"Origin": "http://evil.example"})[0] == 403, "preflight for a web page refused")
ok(call("OPTIONS", "/v1/run", {"Origin": EXT, "Host": "evil.example"})[0] == 403, "preflight host check")
st, hd, body = call("POST", "/v1/run", {"Origin": EXT, "Content-Type": "application/json"}, b'{"query":"gst 2500 18"}')
ok(st == 200 and b"450.00" in body, "extension can run a task")
ok(call("GET", "/v1/health", {"Origin": EXT, "Authorization": "Bearer nope"})[0] == 401, "extension still needs the token")
httpd.shutdown(); B.ALLOWED_ORIGINS.discard(EXT)
ok(B.main("--serve-api", 8799, origins=["http://evil.example"]) == 1, "--allow-origin rejects web addresses")
ok(B.main("--serve-api", 8799, origins=["chrome-extension://x"]) == 1, "--allow-origin rejects short ids")
ok(not B.ORIGIN_OK.fullmatch("https://example.com") and B.ORIGIN_OK.fullmatch(EXT), "origin pattern")

# ---- new tasks
os.chdir(WORK)
(WORK / "s.csv").write_text('item,amount,note\nTea,12.5,hot\nCoffee,30,ok\nCake,"1,200",big\n', encoding="utf-8")
has("csv to json s.csv", "Converted 3 rows", "Columns: item, amount, note")
data = json.loads((WORK / "s.json").read_text())
ok(data[0] == {"item": "Tea", "amount": 12.5, "note": "hot"} and data[1]["amount"] == 30 and isinstance(data[1]["amount"], int), "csv types")
has("csv to json s.csv", "s (1).json")
has("chart csv s.csv", "3 bars", "_chart.html")
page = (WORK / "s_chart.html").read_text()
ok("Tea" in page and "1,200.00" in page and "<script" not in page.lower(), "chart page is static html")
(WORK / "x.csv").write_text("name\n<b>a</b>\n", encoding="utf-8")
has("chart csv x.csv", "No number column", rc=1)
has("profit margin cost 60 price 100", "Margin : 40.0%", "Markup : 66.7%")
has("price for 30% margin cost 70", "Sell at      : 100.00", "Markup       : 42.9%")
has("profit margin cost 0 price 10", "above 0", rc=1)
has("profit margin", "Usage", rc=1)
has("compare loans 500000 8.5% 5y vs 9% 4y", "Loan B costs less overall by 18,254.92", "Loan A has the lower monthly payment")
has("compare loans 100000 0% 2y vs 5% 2y", "Loan A costs less")
has("compare loans 100", "Usage", rc=1)
has("compare loans 100000 500% 2y vs 5% 2y", "Check the values", rc=1)
has("freelance rate income 4000 expenses 800 hours 25 weeks off 6 tax 20", "Hourly rate     : 60.52")
has("freelance rate income 3000", "Hourly rate")
has("freelance rate hours 25", "Usage", rc=1)
has("freelance rate income 3000 hours 200", "Check", rc=1)
essay = "The cat sat on the mat. It was a sunny day and the dog ran in the park with friends. We all went home happy after a long day of fun and games outside."
code, out = jg("readability", input=essay); ok(code == 0 and "Reading ease" in out and "very easy" in out, "readability piped " + out[:80])
(WORK / "essay.txt").write_text(essay)
has("readability essay.txt", "Grade level")
has("readability too short text here", "at least 30 words", rc=1)
# find and replace
(WORK / "docs").mkdir(exist_ok=True)
(WORK / "docs" / "a.txt").write_text("the colour red, colour blue\n"); (WORK / "docs" / "b.md").write_text("no match\n")
(WORK / "docs" / "pic.png").write_bytes(b"\x89PNG colour colour")
has('replace in files docs "colour" with "color"', rc=3)                       # asks first; declined when not interactive
ok((WORK / "docs" / "a.txt").read_text().startswith("the colour"), "declined replace changes nothing")
code, out = jg("--yes", 'replace in files docs "colour" with "color"')
ok(code == 0 and "Replaced 2 place(s) in 1 file(s)" in out, "replace done " + out[:120])
ok((WORK / "docs" / "a.txt").read_text() == "the color red, color blue\n", "text replaced")
ok((WORK / "docs" / "pic.png").read_bytes() == b"\x89PNG colour colour", "binary file untouched")
bk = list((Path(HOME) / "replace_backup").glob("*/a.txt"))
ok(bk and "colour" in bk[0].read_text(), "backup saved")
code, out = jg("--yes", 'replace in files docs "zzzz" with "y"'); ok("Nothing found" in out, "no match message")
code, out = jg("--yes", 'replace in files docs "a" with "b"'); ok(code == 1 and "at least 2" in out, "short search refused")
code, out = jg("--yes", "replace in files docs colour with color"); ok(code == 1 and "Usage" in out, "quotes required")
# watch folder
(WORK / "in").mkdir(exist_ok=True)
for n in ("x.pdf", "y.jpg", "z.crdownload", ".hid.pdf"):
    (WORK / "in" / n).write_text("1"); os.utime(WORK / "in" / n, (time.time() - 60,) * 2)
(WORK / "in" / "fresh.pdf").write_text("1")
code, out = jg("--yes", "watch folder in move pdf to ./out once")
ok(code == 0 and "Moved 1 file(s)" in out and (WORK / "out" / "x.pdf").exists(), "watch moves the finished pdf " + out[:120])
ok((WORK / "in" / "y.jpg").exists() and (WORK / "in" / "z.crdownload").exists() and (WORK / "in" / ".hid.pdf").exists() and (WORK / "in" / "fresh.pdf").exists(), "watch leaves other, partial, hidden and brand-new files")
code, out = jg("--yes", "watch folder in move pdf to ./in once"); ok(code == 1, "same folder refused")
code, out = jg("--yes", "watch folder in"); ok(code == 1 and "Usage" in out, "watch usage")
code, out = jg("watch folder in move pdf to ./out once"); ok(code == 3, "watch asks first")
# exif
try:
    from PIL import Image
    im = Image.new("RGB", (20, 20), "red"); ex = im.getexif(); ex[271] = "Cam"; im.save(WORK / "p.jpg", exif=ex)
    has("strip exif p.jpg", "without hidden data", "camera/time data")
    ok(dict(Image.open(WORK / "p_clean.jpg").getexif()) == {} and dict(Image.open(WORK / "p.jpg").getexif()) == {271: "Cam"}, "exif removed, original kept")
except ImportError:
    has("strip exif p.jpg", "Pillow", rc=1)
# toml
if sys.version_info >= (3, 11):
    (WORK / "c.toml").write_text('[tool]\nname = "x"\nn = 3\n'); out = has("toml to json c.toml", '"name": "x"')
    (WORK / "bad.toml").write_text("= nope"); has("toml to json bad.toml", "Not valid TOML", rc=1)
else:
    has("toml to json c.toml", "3.11", rc=1)

# ---- symlinks are never written through
if hasattr(os, "symlink"):
    outside = WORK / "outside.txt"; outside.write_text("secret colour\n")
    (WORK / "docs2").mkdir(exist_ok=True); (WORK / "docs2" / "real.txt").write_text("colour\n")
    try:
        os.symlink(outside, WORK / "docs2" / "link.txt")
        code, out = jg("--yes", 'replace in files docs2 "colour" with "color"')
        ok(outside.read_text() == "secret colour\n", "replace in files does not write through a symlink")
        ok((WORK / "docs2" / "real.txt").read_text() == "color\n", "regular file in the same folder is changed")
        os.symlink(outside, WORK / "jeeg-report.txt") if not (WORK / "jeeg-report.txt").is_symlink() and not (WORK / "jeeg-report.txt").exists() else None
        (WORK / "jeeg-report.txt").unlink() if (WORK / "jeeg-report.txt").exists() and not (WORK / "jeeg-report.txt").is_symlink() else None
        if not (WORK / "jeeg-report.txt").exists(): os.symlink(outside, WORK / "jeeg-report.txt")
        code, out = jg("report"); ok(outside.read_text() == "secret colour\n" and "link" in out, "report does not write through a symlink")
        (WORK / "jeeg-report.txt").unlink()
    except OSError:
        pass

# ---- send-to installer (Linux/other path, fake home)
fh = tempfile.mkdtemp(prefix="jeeg-sendto-")
env = dict(os.environ, HOME=fh, USERPROFILE=fh, XDG_DATA_HOME=fh + "/.local/share", APPDATA=fh + "/AppData")
inst = str(ROOT / "integrations" / "sendto" / "install.py")
r = subprocess.run([sys.executable, inst, "--dry"], capture_output=True, text=True, env=env); ok(r.returncode == 0 and "Would" in r.stdout, "sendto dry run")
ok(not any(Path(fh).rglob("Send to JeeG")), "dry run writes nothing")
if sys.platform.startswith("linux"):
    r = subprocess.run([sys.executable, inst], capture_output=True, text=True, env=env); f = Path(fh) / ".local/share/nautilus/scripts/Send to JeeG"
    ok(r.returncode == 0 and f.exists() and os.access(f, os.X_OK), "sendto installed")
    f.with_name("f.txt").write_text("a b c\n")
    r = subprocess.run(["sh", str(f), str(f.with_name("f.txt"))], input="word count\n", capture_output=True, text=True, env=env, timeout=60)
    ok("Words: 3" in r.stdout, "sendto script runs a task on the file " + r.stdout[:100])
    r = subprocess.run([sys.executable, inst, "--remove"], capture_output=True, text=True, env=env); ok(not f.exists(), "sendto removed")
body = subprocess.run([sys.executable, "-c", "import sys;sys.path.insert(0,r'%s');import install as i;print(i.windows_body(['C:\\\\x y\\\\jeeg.exe']))" % (ROOT / "integrations" / "sendto")], capture_output=True, text=True).stdout
ok('"C:\\x y\\jeeg.exe" %T% "%~1"' in body and "pause" in body, "windows send-to script quoting")
mac = subprocess.run([sys.executable, "-c", "import sys;sys.path.insert(0,r'%s');import install as i;print(i.mac_script(['/usr/local/bin/jeeg']))" % (ROOT / "integrations" / "sendto")], capture_output=True, text=True).stdout
lin = subprocess.run([sys.executable, "-c", "import sys;sys.path.insert(0,r'%s');import install as i;print(i.linux_body(['jeeg']))" % (ROOT / "integrations" / "sendto")], capture_output=True, text=True).stdout
ok('case "$F" in /*)' in lin, "linux send-to protects file names that start with a dash")
ok("on open theFiles" in mac and "quoted form of POSIX path" in mac, "mac droplet script")

# ---- browser extension files
man = json.loads((ROOT / "integrations/browser/manifest.json").read_text())
ok(man["manifest_version"] == 3 and man["host_permissions"] == ["http://127.0.0.1/*"] and "tabs" not in man["permissions"], "extension manifest is minimal")
for name in ("popup.html", "popup.js", "options.html", "options.js", "README.md"):
    ok((ROOT / "integrations/browser" / name).exists(), "extension file " + name)
ok(not re.search(r"https?://(?!127\.0\.0\.1)", (ROOT / "integrations/browser/popup.js").read_text() + (ROOT / "integrations/browser/options.js").read_text()), "extension contacts only 127.0.0.1")
if shutil.which("node"):
    for n in ("popup.js", "options.js"):
        ok(subprocess.run(["node", "--check", str(ROOT / "integrations/browser" / n)]).returncode == 0, "node syntax " + n)

print(f"v2.9 tests: {P} passed, {F} failed")
sys.exit(1 if F else 0)
