# keywords: keep awake, stay awake, prevent sleep, no sleep, caffeinate, stop sleeping, dont sleep, keep screen on, stop screen sleeping
# desc: Stop the computer sleeping for a while (keep awake 2 hours)
# category: system
# usage: keep awake [2 hours]
# rawargs: yes
import re, shutil, subprocess, sys
from _lib import args_text, WIN, MAC, spawn, fail
t = args_text().lower()
m = re.search(r"(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours|m|min|mins|minute|minutes)?", t)
n = float(m.group(1)) if m else 60
unit = (m.group(2) or "m")[0] if m else "m"
secs = int(n * (3600 if unit == "h" else 60))
if not 60 <= secs <= 86400: fail("Choose between 1 minute and 24 hours, e.g. keep awake 2 hours")
if WIN:
    code = "import ctypes,time;ctypes.windll.kernel32.SetThreadExecutionState(0x80000003);time.sleep(%d)" % secs
    spawn([sys.executable, "-c", code])
elif MAC:
    spawn(["caffeinate", "-dis", "-t", str(secs)])
elif shutil.which("systemd-inhibit"):
    spawn(["systemd-inhibit", "--what=idle:sleep", "--who=TaskRunner", "--why=keep awake", "sleep", str(secs)])
else:
    fail("Needs systemd-inhibit (Linux) - not found.")
print(f"Staying awake for {secs // 3600}h {secs % 3600 // 60}m (it ends by itself).")
