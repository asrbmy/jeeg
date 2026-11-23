# keywords: setup check, check setup, check my setup, check devices and link, devices and link check, are my devices ok
# desc: Check your saved devices, paired computers, bridge rules, ports and optional tools, and say what to fix (setup check). For the basic JeeG self-check use: doctor
# category: system
# usage: setup check
# network: yes
# patterns: ^\s*(?:setup|set up)\s+check\b ;; \bcheck\s+(?:my\s+)?(?:setup|devices and link)\b
# priority: 4
import json, os, platform, shutil, socket, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import data_dir
from _conn import load_reg, split_host
good = bad = 0


def line(ok, text, fix=""):
    global good, bad
    good += ok
    bad += not ok
    print(("  ok    " if ok else "  FIX   ") + text + (f"\n        -> {fix}" if fix and not ok else ""))


def reach(host, port, t=1.2):
    try:
        socket.create_connection((host, port), t).close()
        return True
    except OSError:
        return False


print("Setup check")
d = data_dir()
try:
    p = d / ".doctor.tmp"
    p.write_text("x"); p.unlink()
    line(True, f"data folder is writable ({d})")
except OSError as ex:
    line(False, f"data folder cannot be written ({ex})", "check permissions on that folder, or set JEEG_HOME to another one")
line(sys.version_info >= (3, 9), f"Python {platform.python_version()}", "use Python 3.9 or newer")
try:
    import tkinter  # noqa: F401
    line(True, "window (tkinter) is available")
except ImportError:
    line(True, "window (tkinter) is not installed: only needed for the 'jeeg gui' window")
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import jeeg_policy
    pol = jeeg_policy.load()
    print("  info  " + (jeeg_policy.describe().splitlines()[0] if pol else "no administrator policy is set"))
except Exception:
    pass
# saved things
for label, reg, key in (("smart device", "devices", "ip"), ("MQTT broker", "mqtt", "host"), ("Home Assistant", "homeassistant", "url")):
    for name, v in sorted(load_reg(reg).items()):
        if not isinstance(v, dict):
            continue
        if reg == "homeassistant":
            from urllib.parse import urlparse
            u = urlparse(v.get("url", ""))
            host, port = u.hostname or "", u.port or (443 if u.scheme == "https" else 80)
        elif reg == "mqtt":
            host, port = v.get("host", ""), int(v.get("port", 1883))
        else:
            host, port = split_host(v.get(key, ""), 80)
        line(bool(host) and reach(host, port), f"{label} '{name}' answers", f"check it is on and the address is right ({host}:{port})")
# link
try:
    import jeeg_link, jeeg_chan
    st = jeeg_link.Store(d)
    me = st.identity()
    peers = st.peers()
    print(f"  info  this computer is '{me['name']}', {len(peers)} paired computer(s)")
    for pid, r in sorted(peers.items(), key=lambda x: x[1].get("name", "")):
        if r.get("level") == "full":
            print(f"  warn  '{r.get('name')}' has FULL access to this computer. Change with:  link level {r.get('name')} ask")
        addr = r.get("addr", "")
        if addr:
            h, pt = split_host(addr, jeeg_link.DEFAULT_PORT)
            line(reach(h, pt), f"paired computer '{r.get('name')}' is listening", f"on that computer run:  link listen   (looked at {addr})")
    s = socket.socket()
    try:
        s.bind(("0.0.0.0", jeeg_link.DEFAULT_PORT)); free = True
    except OSError:
        free = False
    s.close()
    print(f"  info  port {jeeg_link.DEFAULT_PORT} is {'free (nothing is listening for pairing right now)' if free else 'in use (probably  link listen  is running)'}")
except ImportError:
    pass
# bridge rules
rules = load_reg("bridge")
brokers = load_reg("mqtt")
for name, r in sorted(rules.items()):
    src = r.get("src", {})
    if src.get("kind") == "mqtt":
        line(src.get("broker") in brokers, f"bridge rule '{name}' has its MQTT broker", f"mqtt add {src.get('broker')} <host>")
    if src.get("kind") in {"webhook", "udp", "tcp"}:
        s = socket.socket()
        try:
            s.bind(("0.0.0.0", int(src.get("port", 0)))); ok = True
        except OSError:
            ok = False
        s.close()
        print(f"  info  bridge rule '{name}' listens on port {src.get('port')} ({'free' if ok else 'in use: probably the bridge is running'})")
# optional tools
for tool, why in (("ffmpeg", "video and audio tasks"), ("tesseract", "reading text from pictures"), ("bluetoothctl", "bluetooth on Linux"), ("ssh", "SSH tasks"), ("git", "git tasks")):
    print(f"  info  {tool}: {'found' if shutil.which(tool) else 'not found (needed for ' + why + ')'}")
for n in ("chrome", "chromium", "google-chrome", "msedge", "microsoft-edge"):
    if shutil.which(n):
        print(f"  info  browser for 'browser' tasks: {n}")
        break
print(f"{good} check(s) fine" + (f", {bad} to fix." if bad else ". Everything looks fine."))
sys.exit(1 if bad else 0)
