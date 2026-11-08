# keywords: my habits, usage report, most used tasks, what do i use most, habit report, usage stats, jeeg stats, shortcut suggestions
# desc: See which phrases and tasks you use most, which often fail, and shortcuts worth saving (my habits; habits month)
# category: utility
# usage: my habits [month|year]
# rawargs: full
# private: yes
# patterns: \bmy\s+habits\b ;; \b(usage|habit)\s+(report|stats|summary)\b ;; \bwhat\s+do\s+i\s+(use|run)\s+(most|the\s+most)\b ;; \bmost\s+used\s+(tasks|phrases)\b ;; \bjeeg\s+stats\b
# priority: 3
import json, re, time
from collections import Counter
from _lib import args_text, data_dir
low = args_text().lower()
days = 30 if re.search(r"\bmonth|30\b", low) else 365 if re.search(r"\byear|all\b", low) else 7
since = time.time() - days * 86400
d = data_dir()
def rows(name):
    out = []
    try:
        for ln in (d / name).read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                x = json.loads(ln)
                if isinstance(x, dict) and x.get("t", 0) >= since:
                    out.append(x)
            except ValueError:
                pass
    except OSError:
        pass
    return out
runs, hist = rows("log.jsonl"), rows("history.jsonl")
if not runs and not hist:
    print("No activity recorded yet. Use JeeG for a while, then ask again:  my habits")
    raise SystemExit(0)
label = {7: "last 7 days", 30: "last 30 days", 365: "this year"}[days]
print(f"Your JeeG habits ({label}) - everything here stays on this computer")
if runs:
    c = Counter(x["s"] for x in runs)
    print(f"  {len(runs)} task runs, {len(c)} different tasks. Most used:")
    for k, n in c.most_common(5):
        print(f"    {k.replace('_', ' '):<26} {n:>4}x")
    fails = []
    for n, k in c.items():
        bad = sum(1 for x in runs if x["s"] == n and x.get("rc", 0) != 0)
        if k >= 3 and bad / k >= 0.3:
            fails.append((bad / k, n, bad, k))
    if fails:
        print("  Often fails (check how you word them: say  tips  or  explain <phrase>):")
        for r, n, bad, k in sorted(fails, reverse=True)[:4]:
            print(f"    {n.replace('_', ' '):<26} failed {bad} of {k} times")
    slow = sorted(((sum(x.get("dt", 0) for x in runs if x["s"] == n) / k, n) for n, k in c.items() if k >= 2), reverse=True)[:2]
    slow = [(t, n) for t, n in slow if t > 3]
    if slow:
        print("  Slowest on average: " + ", ".join(f"{n.replace('_', ' ')} ({t:.1f}s)" for t, n in slow))
    hours = Counter(time.localtime(x["t"]).tm_hour for x in runs)
    if len(runs) >= 10:
        h = hours.most_common(1)[0][0]
        print(f"  Busiest hour: {h:02d}:00-{h:02d}:59")
if hist:
    phrases = Counter(x["q"].strip().lower() for x in hist if x.get("q") and not x["q"].startswith("("))
    rep = [(n, p) for p, n in phrases.items() if n >= 3 and len(p) >= 12]
    if rep:
        print("  Phrases you repeat - save a shortcut with  alias add <short> = <words>:")
        for n, p in sorted(rep, reverse=True)[:4]:
            print(f"    \"{p[:60]}\"  ({n}x)")
try:
    miss = Counter(ln.split("\t")[-1].strip().lower() for ln in (d / "misses.log").read_text(encoding="utf-8", errors="replace").splitlines() if "\t" in ln)
except OSError:
    miss = Counter()
if miss:
    print("  Phrases that matched nothing (say  misses  to see all):")
    for p, n in miss.most_common(3):
        print(f"    \"{p[:60]}\"" + (f"  ({n}x)" if n > 1 else ""))
