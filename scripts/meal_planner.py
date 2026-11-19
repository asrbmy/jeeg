# keywords: meal plan, meal planner, weekly meals, what to cook, menu plan, dinner plan
# desc: Plan the week's meals (meal plan monday dal rice, meal plan, meal today, meal clear)
# category: lists
# usage: meal plan <day> <meals> | meal plan | meal today | meal clear
# rawargs: full
# patterns: ^\s*(meal|meals)\s+(plan|today|clear|tomorrow)\b ;; ^\s*meal\s*plan(ner)?\s*$
# priority: 4
import datetime, re
from _lib import args_text, fail
from _store import load, save
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
t = re.sub(r"^\s*meals?\s*", "", args_text(), flags=re.I).strip()
t = re.sub(r"^plan\s*", "plan ", t, flags=re.I).strip()
d = load("meals.json", {})
words = t.split()
sub = words[0].lower() if words else "plan"
if sub == "clear":
    save("meals.json", {}); print("Meal plan cleared.")
elif sub in {"today", "tomorrow"}:
    day = DAYS[(datetime.date.today().weekday() + (sub == "tomorrow")) % 7]
    print(f"{day.capitalize()}: {d.get(day) or 'nothing planned. Example:  meal plan ' + day + ' dal rice'}")
else:
    rest = words[1:]
    if rest:
        key = next((x for x in DAYS if x.startswith(rest[0].lower()) and len(rest[0]) >= 3), None)
        if not key or len(rest) < 2: fail("Usage: meal plan <day> <meals>   e.g. meal plan monday dal rice")
        d[key] = " ".join(rest[1:])[:100]; save("meals.json", d); print(f"{key.capitalize()}: {d[key]}")
    if not d: fail("Nothing planned yet. Example:  meal plan monday dal rice")
    print("This week's meals:")
    for k in DAYS: print(f"  {k.capitalize():<11}{d.get(k, '-')}")
