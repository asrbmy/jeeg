# keywords: pomodoro, pomo, focus timer, work timer, work sessions, study timer, productivity timer
# desc: Pomodoro focus timer: 25 min work / 5 min break (pomodoro 4 rounds)
# category: reminders
# usage: pomodoro [rounds] [N work] [N break]
# rawargs: yes
import re
from _lib import args_text, notify
from _time import beep, countdown
t = args_text().lower()
def num(pat, default):
    m = re.search(pat, t)
    return float(m.group(1)) if m else default
cycles = int(num(r"(\d+)\s*(?:cycles?|rounds?|sessions?|pomodoros?)", num(r"^\s*(\d+)\b", 4)))
work = num(r"(\d+(?:\.\d+)?)\s*(?:min\w*\s*)?work", 25)
brk = num(r"(\d+(?:\.\d+)?)\s*(?:min\w*\s*)?break", 5)
if not 1 <= cycles <= 12:
    raise SystemExit("Choose 1-12 rounds.")
print(f"Pomodoro: {cycles} round(s), {work:g} min work / {brk:g} min break. Ctrl+C to stop.")
for i in range(1, cycles + 1):
    countdown(work * 60, f"Work {i}/{cycles}  ")
    beep(2); notify("Pomodoro", f"Round {i} done - take a break")
    print(f"Round {i}/{cycles} done.")
    if i < cycles:
        b = brk * 3 if i % 4 == 0 else brk              # long break every 4th round
        countdown(b * 60, f"Break      ")
        beep(1); notify("Pomodoro", "Break over - back to work")
print("All rounds complete. Great work!")
