# keywords: ram, memory, free memory, memory usage, ram usage
# desc: Show RAM usage
# category: system
from _lib import fail, human
from _sys import mem_info
m = mem_info()
if not m:
    fail("Could not read memory information on this system.")
total, free = m
used = total - free
print(f"RAM: {human(used)} used of {human(total)} ({100 * used / total:.0f}%), {human(free)} available")
