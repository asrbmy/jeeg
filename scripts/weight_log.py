# keywords: weight log, log weight, my weight, weigh in, weight history, weight goal, body weight, i weigh
# desc: Log your weight and see the trend (weight 72.5 kg, weight history, weight goal 70)
# category: health
# usage: weight <kg> | weight history | weight goal <kg>
# rawargs: yes
# private: yes
# patterns: ^\s*(log\s+)?(my\s+)?weight\s+\d ;; \bweight\s+(log|history|goal|trend)\b ;; \bi\s+weigh\b ;; \bweigh[\s-]?in\b
# priority: 2
import datetime, re
from _lib import args_text, fail
from _store import load, save
t = args_text().lower()
w = load("weight.json", {})
g = re.search(r"\bgoal\s+(\d+(?:\.\d+)?)", t)
if g:
    v = float(g.group(1))
    if not 20 <= v <= 300: fail("Choose a goal between 20 and 300 kg.")
    w["_goal"] = v; save("weight.json", w); print(f"Goal set to {v:g} kg."); raise SystemExit(0)
m = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kgs|kilos?|lb|lbs|pounds?)?\b", t)
if m and not re.search(r"\b(history|show|trend)\b", t):
    v = float(m.group(1))
    if (m.group(2) or "kg").startswith(("lb", "pound")): v = round(v * 0.45359237, 1)
    if not 20 <= v <= 300: fail("That weight looks wrong (20 to 300 kg).")
    day = datetime.date.today().isoformat()
    w[day] = round(v, 1); save("weight.json", w)
    print(f"Logged {v:g} kg for {day}.")
rows = sorted((k, x) for k, x in w.items() if not k.startswith("_"))[-10:]
if not rows: fail("No weight logged yet. Example:  weight 72.5 kg")
print("Recent: " + ", ".join(f"{k[5:]} {x:g}" for k, x in rows))
if len(rows) > 1:
    d = rows[-1][1] - rows[0][1]
    print(f"Change over these {len(rows)} entries: {d:+.1f} kg")
if "_goal" in w:
    print(f"Goal {w['_goal']:g} kg: {rows[-1][1] - w['_goal']:+.1f} kg to go" if rows[-1][1] != w["_goal"] else "You are at your goal.")
