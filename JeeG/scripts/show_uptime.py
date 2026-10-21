# keywords: uptime, how long on, running time, boot time, since boot, last restart
# desc: Show how long the computer has been on
# category: system
from _lib import fail
from _sys import uptime_seconds
up = uptime_seconds()
if up is None:
    fail("Could not read uptime on this system.")
d, r = divmod(int(up), 86400); h, r = divmod(r, 3600)
print(f"Up for {d} days, {h} hours, {r // 60} minutes")
