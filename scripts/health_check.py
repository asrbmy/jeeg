# keywords: health check, system health, pc health, computer health, is my pc ok, pc checkup, computer checkup
# desc: One-screen check of your computer: disk, memory, CPU, battery, uptime, with warnings
# category: system
# patterns: \b(pc|computer|laptop|system)\s+(health|checkup|check-up)\b ;; \bhealth\s+check\b ;; \bis\s+my\s+(pc|computer|laptop)\s+(ok|okay|fine|healthy)\b
# priority: 2
import os, shutil
from _lib import human
from _sys import mem_info, battery, cpu_percent, uptime_seconds
warn = []
print("Computer health")
try:
    t, u, f = shutil.disk_usage(os.path.expanduser("~"))
    pct = 100 * u / t if t else 0
    print(f"  Disk     {human(u)} used of {human(t)} ({pct:.0f}%), {human(f)} free")
    if pct >= 90 or f < 5 * 1024 ** 3:
        warn.append("The disk is nearly full. Try:  large folders   or   clean temp files")
except OSError:
    print("  Disk     could not be read")
m = mem_info()
if m:
    tot, free = m
    pct = 100 * (tot - free) / tot if tot else 0
    print(f"  Memory   {human(tot - free)} used of {human(tot)} ({pct:.0f}%)")
    if pct >= 90:
        warn.append("Memory is almost full. Try:  running processes")
else:
    print("  Memory   could not be read")
c = cpu_percent()
if c is not None:
    print(f"  CPU      {c:.0f}% busy across {os.cpu_count()} cores")
    if c >= 90:
        warn.append("The CPU is very busy right now. Try:  running processes")
b = battery()
if b:
    print(f"  Battery  {b[0]}% ({b[1]})")
    try:
        if int(b[0]) <= 15 and "disch" in str(b[1]).lower():
            warn.append("The battery is low and not charging.")
    except (TypeError, ValueError):
        pass
up = uptime_seconds()
if up:
    d, r = divmod(int(up), 86400)
    print(f"  Uptime   {d} days {r // 3600} hours")
    if d >= 14:
        warn.append("It has not been restarted for over two weeks. A restart often helps.")
print("\nLooks fine." if not warn else "\nWorth a look:\n  - " + "\n  - ".join(warn))
