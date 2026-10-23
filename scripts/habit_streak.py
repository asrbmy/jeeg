# keywords: habit streak, habits, my habits, streaks, habit list, habit progress, show habits, habit report
# desc: Show all habits with current streak and the last 14 days
# category: habits
import datetime
from _store import load
h = load("habits.json", {})
if not h:
    print("No habits yet. Start with: habit done gym"); raise SystemExit(0)
today = datetime.date.today()
for name, days in sorted(h.items()):
    s = {datetime.date.fromisoformat(d) for d in days}
    cur, d = 0, today if today in s else today - datetime.timedelta(days=1)
    while d in s:
        cur += 1; d -= datetime.timedelta(days=1)
    best = run = 0
    prev = None
    for d in sorted(s):
        run = run + 1 if prev and (d - prev).days == 1 else 1
        best, prev = max(best, run), d
    last14 = "".join("#" if today - datetime.timedelta(days=i) in s else "." for i in range(13, -1, -1))
    print(f"{name:<16} streak {cur:>3}  best {best:>3}  total {len(s):>3}   {last14}")
print("(# = done, . = missed; oldest -> today)")
