# keywords: study log, log study, studied, study time, study report, hours studied, track study, study hours
# desc: Log study time and see where it goes (study log maths 45 min, study report)
# category: productivity
# usage: study log <subject> <time> | study report
# rawargs: yes
# patterns: \bstudy\s+(log|report|hours|time)\b ;; \b(log|logged)\s+(my\s+)?stud(y|ied)\b ;; \bi\s+studied\b
# priority: 2
import datetime, re
from collections import Counter
from _lib import args_text, fail
from _store import load, save
t = args_text().lower()
log = load("study.json", [])
if re.search(r"\b(report|show|summary|total|week|stats|history)\b", t) and not re.search(r"\d", t.replace("week", "")):
    wk = (datetime.date.today() - datetime.timedelta(days=6)).isoformat()
    sub, day = Counter(), Counter()
    for x in log:
        if x["date"] >= wk:
            sub[x["subject"]] += x["min"]; day[x["date"]] += x["min"]
    if not sub:
        fail("No study logged in the last 7 days. Example:  study log maths 45 min")
    print(f"Last 7 days: {sum(sub.values()) / 60:.1f} hours")
    for s, m in sub.most_common():
        print(f"  {s:<18}{m / 60:>5.1f} h  {'#' * max(1, round(m / 30))}")
    print(f"Best day: {max(day, key=day.get)} ({day[max(day, key=day.get)]} min)")
    raise SystemExit(0)
m = re.search(r"(\d+(?:\.\d+)?)\s*(h|hr|hrs|hours?|m|min|mins|minutes?)?\b", t)
if not m:
    fail("Usage: study log <subject> <time>   e.g. study log maths 45 min   |   study report")
v = float(m.group(1)); u = (m.group(2) or "m")[0]
mins = round(v * 60) if u == "h" else round(v)
if not 1 <= mins <= 1440:
    fail("Time must be between 1 minute and 24 hours.")
subject = re.sub(r"\b(study|log|logged|studied|for|hours?|hrs?|mins?|minutes?|today|of|on|a|the)\b|\d+(?:\.\d+)?", " ", t).split()
subject = " ".join(subject)[:40] or "general"
log.append({"date": datetime.date.today().isoformat(), "subject": subject, "min": mins})
save("study.json", log[-5000:])
today = sum(x["min"] for x in log if x["date"] == datetime.date.today().isoformat())
print(f"Logged {mins} min of {subject}. Today so far: {today // 60} h {today % 60} min.")
