"""v2.17: install/uninstall/update/configure apps, watches, network doctor, wifi devices, RSS, save page, share file,
fleet check, sensor log, printers, inventory, sqlite, is-installed, env variables and PATH.
Everything runs against this computer only (fake servers, fake ssh/lp/lpstat/ip commands). Run: python tests/test_v217.py"""
import http.server, json, os, re, sqlite3, stat, subprocess, sys, tempfile, threading, time, urllib.error, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
HOME = tempfile.mkdtemp(prefix="jeeg-v217-")
USERHOME = tempfile.mkdtemp(prefix="jeeg-v217-home-")
WORK = Path(tempfile.mkdtemp(prefix="jeeg-v217-w-"))
BIN = Path(tempfile.mkdtemp(prefix="jeeg-v217-bin-"))
PROFILE = Path(tempfile.mkdtemp(prefix="jeeg-v217-prof-")) / "profile"
os.environ["JEEG_HOME"] = HOME
P = F = 0


def ok(c, label):
    global P, F
    if c:
        P += 1
    else:
        F += 1
        print("FAIL:", label)


def env(extra=None):
    e = dict(os.environ, JEEG_HOME=HOME, HOME=USERHOME, USERPROFILE=USERHOME, NO_PROXY="127.0.0.1,localhost", no_proxy="127.0.0.1,localhost",
             JEEG_TEST_ALLOW_LOCAL="1", JEEG_PROFILE_FILE=str(PROFILE), PATH=str(BIN) + os.pathsep + os.environ.get("PATH", ""))
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"):
        e.pop(k, None)
    e.update(extra or {})
    return e


def jg(*words, yes=False, extra=None, timeout=90):
    a = [sys.executable, str(ROOT / "jeeg.py")] + (["--yes"] if yes else []) + list(words)
    r = subprocess.run(a, capture_output=True, text=True, timeout=timeout, env=env(extra), cwd=WORK, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout + r.stderr


def has(q, *needles, rc=0, absent=(), yes=False, extra=None):
    code, out = jg(q, yes=yes, extra=extra)
    ok(code == rc and all(n in out for n in needles) and not any(a in out for a in absent), f"{q!r} -> rc={code} {out.strip()[:240]!r}")
    return out


def fake(name, body):
    p = BIN / name
    p.write_text("#!/bin/sh\n" + body + "\n")
    p.chmod(p.stat().st_mode | stat.S_IXUSR)
    return p


import jeeg
ok(tuple(int(x) for x in jeeg.__version__.split(".")) >= (2, 17, 0), "version " + jeeg.__version__)

# ================================================================ install / uninstall / update planner (pure)
import _apps
W, M, L = ["winget"], ["brew"], ["apt-get"]
p = _apps.plan("install", "chrome", have=W, osname="windows")
ok(p["cmd"] == ["winget", "install", "--id", "Google.Chrome", "-e"] and not p["sudo"], "winget install chrome " + str(p))
p = _apps.plan("install", "chrome", have=["choco"], osname="windows")
ok(p["cmd"] == ["choco", "install", "googlechrome", "-y"], "choco install chrome")
p = _apps.plan("install", "vlc", have=M, osname="mac")
ok(p["cmd"] == ["brew", "install", "--cask", "vlc"], "brew cask vlc " + str(p))
p = _apps.plan("install", "git", have=M, osname="mac")
ok(p["cmd"] == ["brew", "install", "git"], "brew formula git")
p = _apps.plan("install", "vlc", have=L, osname="linux")
ok(p["cmd"] == ["apt-get", "install", "-y", "vlc"] and p["sudo"], "apt vlc needs sudo " + str(p))
p = _apps.plan("install", "chrome", have=["apt-get", "flatpak"], osname="linux")
ok(p["manager"] == "flatpak" and p["cmd"][:3] == ["flatpak", "install", "-y"], "linux falls back to flatpak for chrome " + str(p))
p = _apps.plan("uninstall", "vlc", have=L, osname="linux")
ok(p["cmd"] == ["apt-get", "remove", "-y", "vlc"], "apt remove")
p = _apps.plan("upgrade", "git", have=W, osname="windows")
ok(p["cmd"][:2] == ["winget", "upgrade"], "winget upgrade")
p = _apps.plan("search", "vlc", have=L, osname="linux")
ok(p["cmd"][0] == "apt-cache" and not p["sudo"], "search never needs sudo")
p = _apps.plan("install", "someunknownthing", have=L, osname="linux")
ok(p["cmd"] == ["apt-get", "install", "-y", "someunknownthing"] and not p["known"], "unknown names are passed as given")
ok("error" in _apps.plan("install", "vlc; rm -rf /", have=L, osname="linux"), "shell characters are refused")
ok("error" in _apps.plan("install", "$(reboot)", have=L, osname="linux"), "command substitution refused")
ok("error" in _apps.plan("install", "--force", have=L, osname="linux"), "option-looking names are refused")
ok("error" in _apps.plan("install", "vlc", have=[], osname="linux"), "no package manager gives a clear error")
ok("error" in _apps.plan("install", "x" * 80, have=L, osname="linux"), "very long names refused")
ok(_apps.split_names("install vlc and the git app, chrome") == ["vlc", "git", "chrome"], "split names " + str(_apps.split_names("install vlc and the git app, chrome")))
ok(len(_apps.split_names(",".join("a%d" % i for i in range(30)))) == 10, "at most 10 apps at once")
ok(_apps.is_preview("vlc preview") and _apps.is_preview("vlc dry-run") and not _apps.is_preview("vlc"), "preview word")
# every catalog entry has at least one package id and a name
ok(len(_apps.CATALOG) >= 40, "catalog has many apps: %d" % len(_apps.CATALOG))
for key, e in _apps.CATALOG.items():
    ok(any(k in e for k in "wcblpaf"), f"catalog entry {key} has a package id")
    for k, v in e.items():
        ok(not re.search(r"[;&|`$<>\s]", v), f"catalog id {key}.{k} has no shell characters: {v}")

# ================================================================ install / uninstall / update through the engine (preview only)
out = has("install vlc preview", "Preview only", "Command:", absent=("done.",))
has("install vlc", rc=3, absent=("Command:",))                                         # asks first, runs nothing
has("uninstall vlc preview", "Preview only", "remove")
has("uninstall vlc", rc=3, absent=("Command:",))
has("update all apps preview", "Preview only")
has("update app git preview", "Preview only", "git")
has("install vlc and git preview", "vlc", "git", "Preview only")
has("install dev bundle preview", "Bundle 'dev'", "git", "Preview only")
has("install nonsense bundle preview", "Bundles:", "dev", "office")
has("search app vlc", "vlc")
has("install $(reboot) preview", "not a name I can use", rc=1)
code, out = jg("install", "vlc;", "touch", "pwned", "preview")
ok(not (WORK / "pwned").exists(), "no shell command injection through install")
has("configure git name Ravi email r@x.com preview", "user.name", "user.email", "Preview only")
has("configure git name Ravi email bad preview", rc=1)
has("configure git", rc=3)                                                             # not previewed, so it asks
code, out = jg("configure git name 'Ravi' email r@x.com; touch pwned2 preview")
ok(not (WORK / "pwned2").exists(), "no injection through configure")
# the engine never runs a package manager when only previewing
fake("apt-get", f"touch {WORK}/apt_ran")
fake("winget", f"touch {WORK}/apt_ran")
jg("install", "vlc", "preview")
ok(not (WORK / "apt_ran").exists(), "preview never starts the package manager")
(BIN / "apt-get").unlink(); (BIN / "winget").unlink()

# ================================================================ installed? (is_installed)
has("is git installed", "installed")
has("which version of python do i have", "installed")
has("is zzzprogramq installed", "not found", "install zzzprogramq", rc=1)
fake("zzfaketool", f"touch {WORK}/fake_ran; echo fake 1.0")
has("is zzfaketool installed", "installed", absent=("fake 1.0",))
ok(not (WORK / "fake_ran").exists(), "an unknown program is only looked up, never run")

# ================================================================ network helpers (pure)
import _netdoc as nd
linux = "192.168.1.1 dev eth0 lladdr aa:bb:cc:dd:ee:01 REACHABLE\n192.168.1.20 dev eth0 lladdr aa:bb:cc:dd:ee:14 STALE\n192.168.1.30 dev eth0  FAILED\n192.168.1.77 dev eth0 lladdr 00:00:00:00:00:00 STALE\n"
r = nd.parse_neighbours(linux)
ok(r == [("192.168.1.1", "aa:bb:cc:dd:ee:01"), ("192.168.1.20", "aa:bb:cc:dd:ee:14")], "ip neigh parsed " + str(r))
mac = "? (192.168.1.1) at 0:1b:2c:3d:4e:5f on en0 ifscope [ethernet]\n? (192.168.1.9) at (incomplete) on en0 ifscope [ethernet]\n? (224.0.0.251) at 1:0:5e:0:0:fb on en0 ifscope permanent [ethernet]\n? (192.168.1.255) at ff:ff:ff:ff:ff:ff on en0 ifscope [ethernet]\n"
r = nd.parse_neighbours(mac)
ok(r == [("192.168.1.1", "00:1b:2c:3d:4e:5f")], "mac arp parsed + padded " + str(r))
win = "Interface: 192.168.1.5 --- 0x7\n  Internet Address      Physical Address      Type\n  192.168.1.1           aa-bb-cc-dd-ee-01     dynamic\n  192.168.1.255         ff-ff-ff-ff-ff-ff     static\n  224.0.0.22            01-00-5e-00-00-16     static\n"
r = nd.parse_neighbours(win)
ok(r == [("192.168.1.1", "aa:bb:cc:dd:ee:01")], "windows arp parsed " + str(r))
ok(nd.parse_neighbours("") == [] and nd.parse_neighbours("garbage\n\x00\n") == [], "empty and garbage input")
ok([i for i, _ in nd.parse_neighbours("10.0.0.10 lladdr aa:aa:aa:aa:aa:aa\n10.0.0.9 lladdr bb:bb:bb:bb:bb:bb\n")] == ["10.0.0.9", "10.0.0.10"], "sorted by address, not text")
h = nd.subnet_hosts("192.168.1.5")
ok(len(h) == 253 and "192.168.1.5" not in h and "192.168.1.1" in h and "192.168.1.254" in h, "private /24 hosts")
ok(nd.subnet_hosts("8.8.8.8") == [] and nd.subnet_hosts("127.0.0.1") == [] and nd.subnet_hosts("1.2.3.4") == [], "public and loopback are never scanned")
ok(len(nd.subnet_hosts("10.1.2.3", 20)) == 20, "limit honoured")
li = nd.local_ip()
ok(li is None or re.fullmatch(r"\d+\.\d+\.\d+\.\d+", li), "local ip shape")
d = nd.diagnose({"local_ip": None})
ok("not on a network" in d[0], "no network")
d = nd.diagnose({"local_ip": "192.168.1.5", "gateway_ok": False})
ok("router" in d[0].lower(), "router down")
d = nd.diagnose({"local_ip": "192.168.1.5", "gateway_ok": True, "dns_ok": False, "internet_ok": False})
ok("nothing reaches the internet" in d[0], "line down")
d = nd.diagnose({"local_ip": "192.168.1.5", "gateway_ok": True, "dns_ok": True, "internet_ok": False})
ok("unreachable" in d[0], "dns ok, no internet")
d = nd.diagnose({"local_ip": "192.168.1.5", "gateway_ok": True, "dns_ok": False, "internet_ok": True})
ok("DNS" in d[0] and any("flush dns" in t for t in d[1]), "dns problem suggests flush dns")
d = nd.diagnose({"local_ip": "192.168.1.5", "gateway_ok": True, "dns_ok": True, "internet_ok": True, "internet_ms": 300, "dns_ms": 20})
ok("slow" in d[0], "slow link")
d = nd.diagnose({"local_ip": "192.168.1.5", "gateway_ok": None, "dns_ok": True, "internet_ok": True, "internet_ms": 20, "dns_ms": 20})
ok("fine" in d[0] and d[1] == [], "all fine")
pr, df = nd.parse_lpstat("printer Office_HP is idle.  enabled since Mon 10 Nov 2026\nprinter Label now printing Label-12.  enabled since Mon\nprinter Old disabled since Mon\nsystem default destination: Office_HP\n")
ok(pr == [("Office_HP", "idle"), ("Label", "printing"), ("Old", "disabled")] and df == "Office_HP", "lpstat parsed " + str(pr))
ok(nd.parse_lpstat("") == ([], None), "empty lpstat")
ok(nd.parse_powershell_printers("Microsoft Print to PDF  Normal\nHP LaserJet 400  Offline\n\n") == [("Microsoft Print to PDF", "Normal"), ("HP LaserJet 400", "Offline")], "powershell printers")

# ================================================================ network doctor and wifi devices (smoke: no crash, sensible words)
code, out = jg("network doctor", timeout=60)
ok(code in (0, 1) and "Network doctor" in out and "This computer" in out and "Traceback" not in out, "network doctor runs: " + out[:200])
fake("ip", 'if [ "$1" = "neigh" ]; then echo "192.168.1.1 dev eth0 lladdr aa:bb:cc:dd:ee:01 REACHABLE"; echo "192.168.1.20 dev eth0 lladdr aa:bb:cc:dd:ee:14 STALE"; fi')
if sys.platform.startswith("linux"):
    code, out = jg("who is on my wifi")
    ok(code == 0 and "aa:bb:cc:dd:ee:01" in out and "192.168.1.20" in out and "2 device(s)" in out or "not on a network" in out, "wifi devices listed: " + out[:200])
(BIN / "ip").unlink()

# ================================================================ local web servers for rss / save page / watch
FEED = """<?xml version="1.0"?><rss version="2.0"><channel><title>Test Blog</title>
<item><title>First &amp; best</title><link>http://127.0.0.1/a</link><pubDate>Mon, 10 Nov 2026 10:00:00 GMT</pubDate></item>
<item><title>Second post</title><link>http://127.0.0.1/b</link></item></channel></rss>"""
ATOM = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>Atom Site</title>
<entry><title>Atom one</title><link href="http://127.0.0.1/x"/><updated>2026-11-01T10:00:00Z</updated></entry></feed>"""
BOMB = """<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;&lol;&lol;">]><rss><channel><title>&lol2;</title></channel></rss>"""
PAGE = "<html><head><title>My Article</title><style>p{color:red}</style><script>var secret=1;</script></head><body><nav>MENU</nav><h1>Big Heading</h1><p>Hello <b>world</b>, this is the article text.</p><footer>FOOT</footer></body></html>"
state = {"price": "Price: $50", "page": "one"}


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        body, ct = {"/feed.xml": (FEED, "application/rss+xml"), "/atom.xml": (ATOM, "application/atom+xml"), "/bomb.xml": (BOMB, "text/xml"),
                    "/article": (PAGE, "text/html"), "/empty": ("<html><body></body></html>", "text/html"),
                    "/notfeed": ("<html><body>hello</body></html>", "text/html"),
                    "/item": (f"<html><body>{state['price']}</body></html>", "text/html"),
                    "/news": (f"<html><body>news {state['page']}</body></html>", "text/html")}.get(self.path, (None, None))
        if body is None:
            self.send_error(404)
            return
        b = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", ct + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{srv.server_address[1]}"

# ---- rss
has("feed list", "No feeds yet", rc=1)
has(f"feed add {BASE}/feed.xml Blog", "Following Blog", "2 items")
has(f"feed add {BASE}/feed.xml", "already", rc=1)
has(f"feed add {BASE}/atom.xml", "Following Atom Site", "1 items")
has(f"feed add {BASE}/bomb.xml", rc=1, absent=("Following",))
has(f"feed add {BASE}/notfeed", "not an RSS", rc=1)
has(f"feed add {BASE}/missing.xml", "Could not download", rc=1)
has("feed add ftp://example.com/x", rc=1)
has("feed add https://user:pw@example.com/f.xml", rc=1)
o = has("read my feeds", "Blog", "First & best", "Second post", "Atom one", absent=("Traceback",))
o = has("feed list", "1. Blog", "2. Atom Site")
has("read my feeds 1", "First & best")
has("feed remove 5", "No feed number", rc=1)
has("feed remove 1", "Removed Blog")
has("feed list", "1. Atom Site", absent=("Blog",))
ok(json.loads((Path(HOME) / "feeds.json").read_text())[0]["url"].endswith("/atom.xml"), "feeds saved to disk")

# ---- save page
code, out = jg(f"save page {BASE}/article")
ok(code == 0 and "Saved" in out, "save page: " + out[:200])
saved = list(Path(USERHOME).rglob("*.txt"))
txt = saved[0].read_text(encoding="utf-8") if saved else ""
ok("My Article" in txt and "Big Heading" in txt and "article text" in txt and "secret" not in txt and "MENU" not in txt and "color:red" not in txt, "saved text is clean: " + txt[:200])
has(f"save page {BASE}/empty", "no readable text", rc=1)
has(f"save page {BASE}/missing", "Could not download", rc=1)
has("save page not-a-url", rc=1)

# ---- watch (existing task, now covered)
has("watch list", "Nothing is being watched")
has(f"watch price {BASE}/item Shoe", "Watching", "Shoe")
has(f"watch page {BASE}/news News", "Watching")
has(f"watch page {BASE}/news", "already", rc=1)
has("watch site https://example.invalid/", rc=0)                                       # added even if unreachable
has("check watches", "0 change(s)")
state["price"], state["page"] = "Price: $40", "two"
has("check watches", "price dropped from 50 to 40", "the page changed", "2 change(s)")
has("check watches", "0 change(s)")
has("watch list", "Shoe", "News")
has("watch remove 9", rc=1)
has("watch remove 1", "Stopped watching")
has("watch release not-a-repo", rc=1)
has("watch ssl not_valid!", rc=1)
has("watch page file:///etc/passwd", rc=1)
has("ssl expiry", "Say which site", rc=1)

# ================================================================ share file
(WORK / "secret.txt").write_bytes(b"the secret contents\n" * 50)
pr = subprocess.Popen([sys.executable, str(ROOT / "jeeg.py"), "send", "secret.txt", "to", "my", "phone"], cwd=WORK, env=env({"JEEG_SHARE_LOCAL": "1", "JEEG_SHARE_SECONDS": "30"}),
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, stdin=subprocess.DEVNULL)
url, head = None, ""
t0 = time.time()
while time.time() - t0 < 20 and not url:
    ln = pr.stdout.readline()
    head += ln
    m = re.search(r"(http://127\.0\.0\.1:\d+/\S+)", ln)
    if m:
        url = m.group(1)
ok(url is not None, "share prints a link: " + head[:200])
if url:
    base = url.rsplit("/", 2)[0]
    for bad in (base + "/", base + "/wrongtoken/secret.txt", url + "x", url.rsplit("/", 1)[0] + "/other.txt"):
        try:
            urllib.request.urlopen(urllib.request.Request(bad), timeout=5)
            ok(False, "wrong link must be refused: " + bad)
        except urllib.error.HTTPError as ex:
            ok(ex.code == 404, f"wrong link gives 404 not {ex.code}")
    with urllib.request.urlopen(url, timeout=5) as r:
        data = r.read()
    ok(data == (WORK / "secret.txt").read_bytes(), "the file downloads intact")
    try:
        pr.wait(15)
    except subprocess.TimeoutExpired:
        pr.kill()
    ok(pr.returncode == 0, "sharing stops after one download, rc=%s" % pr.returncode)
    try:
        urllib.request.urlopen(url, timeout=3)
        ok(False, "second download must fail")
    except (urllib.error.URLError, OSError):
        ok(True, "second download refused")
else:
    pr.kill()
has("send nothere.pdf to my phone", "Say which file", rc=1)
# short timeout: stops by itself
t0 = time.time()
pr = subprocess.run([sys.executable, str(ROOT / "jeeg.py"), "send", "secret.txt", "to", "my", "phone"], cwd=WORK, env=env({"JEEG_SHARE_LOCAL": "1", "JEEG_SHARE_SECONDS": "1"}),
                    capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
ok(pr.returncode == 0 and "Time is up" in pr.stdout and time.time() - t0 < 25, "sharing stops by itself: " + pr.stdout[-120:])

# ================================================================ sensor log
has("show readings temperature", "No readings", rc=1)
has("log reading temperature 24.5 c", "Logged temperature = 24.5 c", "1 readings")
has("log reading temperature 26", "2 readings")
has("alert when temperature above 30", "warn you when temperature goes above 30")
has("log reading temperature 29", absent=("ALERT",))
has("log reading temperature 31.5", "ALERT: temperature is 31.5, above your limit of 30")
has("alert when humidity below 40", "humidity goes below 40")
has("log reading humidity 55", absent=("ALERT",))
has("log reading humidity 35", "ALERT: humidity is 35, below your limit of 40")
o = has("show readings temperature", "4 readings", "min 24.5", "avg 27.75", "max 31.5", "last 31.5", "Alert: warn when above 30")
o = has("readings chart temperature", "*", "31.50", "24.50", "+---")
ok(len([l for l in o.splitlines() if "|" in l]) == 8, "chart has 8 rows")
has("list readings", "temperature: 4 readings", "humidity: 2 readings")
has("show readings temperature today", "4 readings")
has("log reading bad name! 5", rc=1)
has("log reading temperature abc", rc=1)
for i in range(70):                                                                    # chart shrinks to 60 columns
    jg("log", "reading", "wind", str(i))
o = has("readings chart wind", "70 readings")
ok(max(len(l) for l in o.splitlines() if "|" in l) <= 12 + 60, "chart is at most 60 wide")
ok(json.loads((Path(HOME) / "readings.json").read_text())["series"]["temperature"][0][1] == 24.5, "readings stored")

# ================================================================ inventory
has("stock list", "No stock yet", rc=1)
has("stock add rice 20 min 5", "rice: 20 in stock", "warn at 5")
has("stock add rice 5", "rice: 25 in stock")
has("stock add sugar 3 min 4", "sugar: 3 in stock")
has("stock add  dal 2.5", "dal: 2.5 in stock")
has("stock sell rice 20", "rice: 5 left", "LOW")
has("stock sell rice 6", "Only 5 of rice", rc=1)
has("stock sell milk 1", "No item", rc=1)
has("low stock", "2 item(s) to buy", "rice", "sugar", absent=("dal",))
has("stock list", "3 item(s)", "rice", "sugar", "dal")
has("stock set rice 50 min 10", "rice: set to 50")
has("low stock", "sugar", absent=("rice",))
has("stock delete sugar", "Removed sugar")
has("stock delete sugar", rc=1)
has("stock add rice abc", rc=1)
has("stock sell rice -3", rc=1)
ok(json.loads((Path(HOME) / "inventory.json").read_text())["rice"] == {"qty": 50.0, "min": 10.0}, "inventory saved")

# ================================================================ sqlite (read only)
db = WORK / "shop.db"
con = sqlite3.connect(db)
con.execute("CREATE TABLE sales (id INTEGER PRIMARY KEY, item TEXT, qty INTEGER)")
con.executemany("INSERT INTO sales (item, qty) VALUES (?, ?)", [("pen", 3), ("book", 1), ("bag", None)] + [(f"x{i}", i) for i in range(300)])
con.execute("CREATE VIEW big AS SELECT * FROM sales WHERE qty > 100")
con.commit(); con.close()
has("database tables shop.db", "sales  (303 rows): id, item, qty", "big: id, item, qty")
has("query database shop.db select * from sales limit 2", "pen", "book", "2 row(s)")
has("query database shop.db select item, qty from sales where qty is null", "bag", "1 row(s)")
has("query database shop.db select count(*) as n from sales", "303")
o = has("query database shop.db select * from sales", "200 row(s)", "stopped at 200")
has("query database shop.db with t as (select 1 as a) select a from t", "1 row(s)")
for bad in ("insert into sales (item) values ('x')", "delete from sales", "drop table sales", "update sales set qty = 0",
            "select 1; drop table sales", "attach database 'x.db' as x", "pragma writable_schema = 1", "create table z (a)", "vacuum"):
    code, out = jg("query", "database", "shop.db", bad)
    ok(code == 1 and "Traceback" not in out, f"refused: {bad!r} -> {out.strip()[:100]!r}")
con = sqlite3.connect(db)
ok(con.execute("select count(*) from sales").fetchone()[0] == 303 and con.execute("select name from sqlite_master where name='sales'").fetchone(), "the database is untouched")
con.close()
has("query database shop.db select * from nothere", "The database said", rc=1)
(WORK / "fake.db").write_text("not a database at all")
has("database tables fake.db", "not a SQLite database", rc=1)
has("database tables missing.db", "No file named", rc=1)
(WORK / "empty.db").write_bytes(b"")
has("database tables empty.db", rc=1)

# ================================================================ printers
fake("lpstat", 'echo "printer Office_HP is idle.  enabled since Mon 10 Nov 2026"; echo "system default destination: Office_HP"')
has("printer status", "1 printer(s)", "Office_HP  -  idle", "(default)")
fake("lpstat", "")
has("list printers", "No printers found")
(BIN / "lpstat").unlink()
(WORK / "doc.txt").write_text("print me")
fake("lp", f'echo "$@" > {WORK}/lp_args; echo "request id is Office_HP-1 (1 file(s))"')
has("print doc.txt", rc=3)                                                             # asks first
has("print doc.txt preview", "Command:", "Preview only", absent=("request id",))
ok(not (WORK / "lp_args").exists(), "preview never prints")
has("print doc.txt", "request id", yes=True)
ok((WORK / "lp_args").exists() and "doc.txt" in (WORK / "lp_args").read_text(), "lp got the file")
has("print missing.pdf", "Say which file", rc=1, yes=True)
(BIN / "lp").unlink()

# ================================================================ environment variables and PATH
PROFILE.write_text("# my own settings\nalias ll='ls -l'\n")
before = PROFILE.read_text()
has("set env variable API_URL to https://x.com/a?b=1&c=2 preview", "Would add", "export API_URL=")
ok(PROFILE.read_text() == before, "preview does not write")
has("set env variable API_URL to https://x.com", rc=3)
ok(PROFILE.read_text() == before, "unconfirmed does not write")
has("set env variable API_URL to https://x.com/a?b=1&c=2", "Saved API_URL", yes=True)
t = PROFILE.read_text()
ok(t.startswith(before) and "# jeeg:env API_URL\nexport API_URL='https://x.com/a?b=1&c=2'\n" in t, "block written, file kept: " + repr(t))
ok((PROFILE.parent / "profile.jeeg-backup").read_text() == before, "backup of the old file")
has("set env variable API_URL to http://other", "Saved", yes=True)
t = PROFILE.read_text()
ok(t.count("API_URL") == 2 and "export API_URL=http://other" in t, "second set replaces, not duplicates: " + repr(t))
has("set env variable MSG to hello world $HOME `id` \"q\"", "Saved MSG", yes=True)
sh = subprocess.run(["sh", "-c", f". {PROFILE}; printf %s \"$MSG\""], capture_output=True, text=True, env=dict(os.environ, HOME=USERHOME))
ok(sh.stdout == 'hello world $HOME `id` "q"', "value is quoted safely, nothing expands: " + repr(sh.stdout))
for bad in ("set env variable 1ABC to x", "set env variable PATH to /evil", "set env variable LD_PRELOAD to /evil.so", "set env variable DYLD_INSERT_LIBRARIES to /x",
            "set env variable A-B to x", "set env variable X to"):
    code, out = jg(bad, yes=True)
    ok(code in (1, 2), f"refused: {bad!r} -> {code} {out.strip()[:80]!r}")
ok("evil" not in PROFILE.read_text() and "1ABC" not in PROFILE.read_text(), "bad variables never reach the file")
has("remove env variable API_URL", "Removed API_URL", yes=True)
t = PROFILE.read_text()
ok("API_URL" not in t and "alias ll='ls -l'" in t and "# my own settings" in t, "removal keeps the rest: " + repr(t))
has("remove env variable NEVER_SET", "left it alone", rc=1, yes=True)
has("remove env variable MSG preview", "Would remove", yes=True)
ok("MSG" in PROFILE.read_text(), "preview removal keeps it")
tools = WORK / "my tools"
tools.mkdir(exist_ok=True)
has(f"add {tools} to path preview", "Would add", yes=True)
has(f"add {tools} to path", "Done", yes=True)
t = PROFILE.read_text()
ok(f"export PATH='{tools}':\"$PATH\"" in t, "path line quoted: " + repr(t[-120:]))
sh = subprocess.run(["sh", "-c", f". {PROFILE}; printf %s \"$PATH\""], capture_output=True, text=True, env=dict(os.environ, HOME=USERHOME))
ok(sh.stdout.startswith(str(tools) + ":"), "PATH works when sourced")
has(f"add {WORK}/nothere to path", "not a folder", rc=1, yes=True)
has("add /tmp/a;b to path", rc=1, yes=True)

# ================================================================ fleet check (fake ssh)
has("check all computers", "No saved computers", rc=1, yes=True)
has("check all computers", rc=3)
jg("computer", "add", "pi", "pi@192.168.1.20")
jg("computer", "add", "nas", "admin@192.168.1.30")
jg("computer", "add", "ghost", "me@192.168.1.99")
fake("ssh", '''case "$*" in
  *pi@*) printf 'Computer health\\n  Disk     10 GB used of 32 GB (31%%)\\n  Uptime   3 days 2 hours\\n\\nLooks fine.\\n'; exit 0;;
  *admin@*) echo "jeeg: command not found"; exit 127;;
  *) exit 255;;
esac''')
code, out = jg("check all computers", yes=True)
ok(code == 1 and "pi:" in out and "Disk     10 GB" in out and "Looks fine." in out, "fleet healthy machine shown: " + out[:300])
ok("nas: PROBLEM" in out and "ghost: PROBLEM" in out and "could not connect" in out, "fleet problems named: " + out[-300:])
ok("1 of 3 computers answered" in out, "fleet summary: " + out[-100:])
(BIN / "ssh").unlink()

# ================================================================ no network code leaks into places it should not
for f in ("scan_network.py", "network_doctor.py", "share_file.py", "rss_feed.py", "save_page.py", "fleet_check.py"):
    ok(re.search(r"^# network:\s*yes\s*$", (ROOT / "scripts" / f).read_text(encoding="utf-8"), re.M) is not None, f + " is tagged network")
ok("0.0.0.0" not in (ROOT / "scripts" / "share_file.py").read_text(), "share_file never binds to all interfaces")
ok("shell=True" not in "".join((ROOT / "scripts" / f).read_text() for f in ("_apps.py", "install_app.py", "uninstall_app.py", "update_apps.py", "install_bundle.py", "configure_app.py", "fleet_check.py", "print_file.py", "env_variable.py")), "no shell=True in the new tasks")

srv.shutdown()
print(f"v2.17 tests: {P} passed, {F} failed")
sys.exit(1 if F else 0)
