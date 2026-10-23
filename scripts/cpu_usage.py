# keywords: cpu, processor, cpu usage, load, cpu load, busy
# desc: Show current CPU load
# category: system
import os
from _lib import fail
from _sys import cpu_percent
p = cpu_percent()
if p is None:
    fail("Could not read CPU load on this system.")
print(f"CPU: {p:.0f}% busy across {os.cpu_count()} logical cores")
