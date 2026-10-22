# keywords: briefing, brief me, agenda, summary, overview
# desc: Daily briefing (say: morning briefing): date, weather, to-dos, birthdays, reminders
# category: routines
# usage: daily briefing [city]
import json, time
from _lib import args_text, data_dir
import urllib.parse
from _net import get
from _time import load_reminders
print(time.strftime("%A, %d %B %Y   %I:%M %p"))
city = "+".join(x for x in args_text().split() if x.lower() not in ("morning", "daily", "my", "today", "the", "evening"))
wx = get(f"https://wttr.in/{urllib.parse.quote(city, safe="+")}?format=3", timeout=6)
print("Weather :", wx.strip() if wx else "(offline)")
d = data_dir()
todos = json.loads((d / "todos.json").read_text(encoding="utf-8")) if (d / "todos.json").exists() else []
open_t = [t for t in todos if not t["done"]]
print(f"To-dos  : {len(open_t)} open" + ("" if open_t else " - nothing pending"))
for t in open_t[:8]:
    print(f"   [ ] {t['id']:>3}  {t['text']}")
bd = d / "birthdays.json"
if bd.exists():
    today = time.localtime()
    soon = []
    for name, v in json.loads(bd.read_text(encoding="utf-8")).items():
        mm, dd = int(v["date"][:2]), int(v["date"][3:5])
        try:
            nxt = time.mktime((today.tm_year, mm, dd, 0, 0, 0, 0, 0, -1))
            if nxt < time.mktime((today.tm_year, today.tm_mon, today.tm_mday, 0, 0, 0, 0, 0, -1)):
                nxt = time.mktime((today.tm_year + 1, mm, dd, 0, 0, 0, 0, 0, -1))
        except (ValueError, OverflowError):
            continue
        days = round((nxt - time.time()) / 86400 + 0.5)
        if days <= 7:
            soon.append((days, name))
    for days, name in sorted(soon):
        print(f"Birthday: {name.title()} " + ("TODAY!" if days <= 0 else f"in {days} day(s)"))
r = load_reminders()
if r:
    print(f"Reminders: {len(r)} active")
