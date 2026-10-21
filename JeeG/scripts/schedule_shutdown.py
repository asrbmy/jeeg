# keywords: schedule shutdown, shutdown after, shutdown in, auto shutdown, shutdown timer, sleep timer
# desc: Shut down after N minutes (schedule shutdown 45 minutes)
# category: power
# usage: schedule shutdown <minutes>
# confirm: yes
import re, subprocess
from _lib import WIN, args_text, fail
m = re.search(r"\d+", args_text())
if not m or not 1 <= int(m.group()) <= 1440:
    fail("Give minutes (1-1440), e.g. schedule shutdown 45 minutes")
n = int(m.group())
if "hour" in args_text().lower():
    n *= 60
    if n > 1440: fail("Maximum is 24 hours.")
rc = subprocess.call(["shutdown", "/s", "/t", str(n * 60)] if WIN else ["shutdown", "-h", f"+{n}"])
if rc:
    fail("Could not schedule the shutdown (administrator rights may be needed).")
print(f"Shutdown scheduled in {n} minutes. Cancel with: cancel shutdown")
