# keywords: water log, log water, drank water, water intake, water today, how much water, water goal, hydration log, track water
# desc: Log water you drank and see today's total (water log 500 ml, water log 2 glasses, water today, water goal 3000)
# category: health
# usage: water log <amount> [ml|glasses|bottles] | water today | water goal <ml>
# rawargs: yes
import datetime, re
from _lib import args_text, fail
from _store import load, save
t = args_text().lower()
w = load("water.json", {})
today = datetime.date.today().isoformat()
goal = int(w.get("_goal", 2500))
m = re.search(r"\bgoal\s+(\d+(?:\.\d+)?)\s*(l|litres?|liters?|ml)?", t)
if m:
    v = float(m.group(1)); ml = v * 1000 if (m.group(2) or "ml").startswith("l") and v < 20 else v
    if not 500 <= ml <= 10000: fail("Choose a goal between 500 ml and 10,000 ml.")
    w["_goal"] = int(ml); save("water.json", w); print(f"Daily goal set to {int(ml):,} ml."); raise SystemExit(0)
m = re.search(r"(\d+(?:\.\d+)?)\s*(ml|millilit\w*|l|lit\w*|glass(?:es)?|bottles?|cups?|sips?)?", t)
if m and not re.search(r"\b(today|show|total)\b", t) or (m and m.group(2)):
    v = float(m.group(1)); u = (m.group(2) or "ml")
    mult = {"ml": 1, "mi": 1, "l": 1000, "li": 1000, "gl": 250, "bo": 500, "cu": 240, "si": 30}
    ml = v * mult.get(u[:2], 1)
    if not 10 <= ml <= 5000: fail("That amount looks wrong (10 ml to 5 litres at a time).")
    w[today] = round(w.get(today, 0) + ml); save("water.json", w)
    print(f"Logged {ml:,.0f} ml.")
tot = w.get(today, 0)
print(f"Today: {tot:,.0f} ml of your {goal:,} ml goal ({tot / goal * 100:.0f}%). Change the goal with:  water goal 3000")
