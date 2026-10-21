# keywords: system, info, computer, specs, pc, hardware, configuration, about, details
# desc: Show OS, CPU, memory, disk and uptime
# category: system
import os, platform, shutil, socket
from _lib import human
from _sys import mem_info, uptime_seconds
print(f"Computer : {socket.gethostname()}")
print(f"OS       : {platform.system()} {platform.release()} ({platform.machine()})")
print(f"CPU      : {platform.processor() or 'unknown'}, {os.cpu_count()} logical cores")
m = mem_info()
if m:
    print(f"Memory   : {human(m[0])} total, {human(m[1])} free")
t, u, f = shutil.disk_usage(os.path.abspath(os.sep))
print(f"Disk     : {human(u)} used of {human(t)} ({human(f)} free)")
up = uptime_seconds()
if up:
    d, r = divmod(int(up), 86400); h, r = divmod(r, 3600)
    print(f"Uptime   : {d}d {h}h {r // 60}m")
print(f"Python   : {platform.python_version()}")
