# keywords: track start, track stop, track status, track report, start tracking, stop tracking
# desc: Track how long you work on things (track start report, track stop, track status, track report week)
# category: productivity
# usage: track start <task> | track stop | track status | track report [today|week]
# rawargs: full
# patterns: ^\s*track\s+(start|stop|status|report|now)\b
# priority: 4
import datetime, re
from _lib import args_text, fail
from _store import load, save
t = re.sub(r"^\s*(?:track|time)\s*", "", args_text(), flags=re.I).strip()
sub, _, body = t.partition(" ")
sub, body = sub.lower(), body.strip()
d = load("timetrack.json", {"running": None, "log": []})
now = datetime.datetime.now().replace(microsecond=0)
def fmt(s):
    s = int(s); return f"{s // 3600}h {s % 3600 // 60:02d}m"
def stop():
    r = d["running"]
    secs = (now - datetime.datetime.fromisoformat(r["start"])).total_seconds()
    d["log"].append({"task": r["task"], "start": r["start"], "secs": int(secs)})
    d["log"] = d["log"][-3000:]; d["running"] = None
    return r["task"], secs
if sub == "start":
    if not body: fail("Usage: track start <task>")
    if d["running"]:
        n, s = stop(); print(f"Stopped {n} ({fmt(s)}).")
    d["running"] = {"task": body[:60].lower(), "start": now.isoformat()}
    save("timetrack.json", d); print(f"Tracking '{body[:60].lower()}' from {now:%H:%M}. Stop with:  track stop")
elif sub == "stop":
    if not d["running"]: fail("Nothing is being tracked.")
    n, s = stop(); save("timetrack.json", d); print(f"Stopped {n}: {fmt(s)}.")
elif sub == "status" or sub == "now":
    if d["running"]:
        s = (now - datetime.datetime.fromisoformat(d["running"]["start"])).total_seconds()
        print(f"Tracking '{d['running']['task']}' for {fmt(s)}.")
    else: print("Nothing is being tracked. Start with:  track start <task>")
else:
    week = "week" in body or "week" in t
    since = (now - datetime.timedelta(days=6)).replace(hour=0, minute=0, second=0) if week else now.replace(hour=0, minute=0, second=0)
    tot = {}
    for e in d["log"]:
        if datetime.datetime.fromisoformat(e["start"]) >= since: tot[e["task"]] = tot.get(e["task"], 0) + e["secs"]
    if not tot: fail("No tracked time " + ("this week." if week else "today."))
    print("This week:" if week else "Today:")
    for k, v in sorted(tot.items(), key=lambda x: -x[1]): print(f"  {k:<28}{fmt(v)}")
    print(f"  Total {fmt(sum(tot.values()))}")
