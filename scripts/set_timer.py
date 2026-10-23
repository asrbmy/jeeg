# keywords: timer, countdown, after, minutes, seconds, minute, second, hours
# desc: Countdown timer with a beep (set timer 10 minutes tea)
# category: time
# usage: set timer <duration> [label]
# rawargs: yes
import re, sys, time
from _lib import args_text, fail, notify, WIN
t = args_text().lower()
units = {"h": 3600, "hr": 3600, "hour": 3600, "hours": 3600, "m": 60, "min": 60, "mins": 60, "minute": 60,
         "minutes": 60, "s": 1, "sec": 1, "secs": 1, "second": 1, "seconds": 1}
parts = re.findall(r"(\d+(?:\.\d+)?)\s*([a-z]+)", t)
secs, used = 0.0, []
for n, u in parts:
    if u in units:
        secs += float(n) * units[u]; used.append(f"{n} {u}")
if not secs:
    m = re.search(r"\d+(?:\.\d+)?", t)     # bare number = minutes
    if m: secs = float(m.group()) * 60
if secs <= 0:
    fail("Say how long: set timer 10 minutes   (or 90 seconds, 1 hour 30 minutes)")
if secs > 86400:
    fail("Timers are limited to 24 hours.")
label = re.sub(r"(\d+(?:\.\d+)?)\s*(" + "|".join(sorted(units, key=len, reverse=True)) + r")\b", "", t).strip(" ,.-")
end = time.time() + secs
print(f"Timer set for {int(secs // 60)}m {int(secs % 60)}s" + (f" - {label}" if label else "") + ".  Ctrl+C to cancel.")
try:
    while True:
        left = end - time.time()
        if left <= 0: break
        sys.stdout.write(f"\r  {int(left // 3600):02d}:{int(left % 3600 // 60):02d}:{int(left % 60):02d} left ")
        sys.stdout.flush()
        time.sleep(min(0.5, left))
except KeyboardInterrupt:
    fail("\nTimer cancelled.", 130)
print("\r  Time is up!" + (f"  ({label})" if label else "") + "          ")
notify("Timer finished", label or "Time is up")
for _ in range(3):
    if WIN:
        import winsound; winsound.Beep(1000, 300)
    else:
        sys.stdout.write("\a"); sys.stdout.flush()
    time.sleep(0.4)
