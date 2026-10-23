# keywords: stopwatch, stop watch, measure time, lap, elapsed
# desc: Start a stopwatch (press Enter to stop)
# category: time
import sys, time
from _lib import fail
if not sys.stdin.isatty():
    fail("The stopwatch needs an interactive terminal.")
input("Press Enter to START... ")
t0 = time.perf_counter()
laps = []
while True:
    s = input("Enter = lap, 's' + Enter = stop: ").strip().lower()
    now = time.perf_counter() - t0
    if s == "s":
        break
    laps.append(now)
    print(f"  lap {len(laps)}: {now:.2f}s")
print(f"Total: {now:.2f}s ({int(now // 60)}m {now % 60:.1f}s)")
