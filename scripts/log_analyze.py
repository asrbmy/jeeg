# keywords: log analyze, analyze log, log summary, log errors, count errors in log, summarize log file, log file report
# desc: Summarise a log file: counts by level, the most common errors, and the busiest minutes (log analyze app.log)
# category: developer
# usage: log analyze <file>
# rawargs: full
# patterns: ^\s*(?:log\s+analy[sz]e|analy[sz]e\s+(?:the\s+)?log|log\s+summary)\b
# priority: 3
import re, collections
from _lib import args_text, fail
from _files import path_arg
t = re.sub(r"^\s*(?:log\s+analy[sz]e|analy[sz]e\s+(?:the\s+)?log(?:\s+file)?|log\s+summary)\s*(?:of|for)?\s*", "", args_text(), flags=re.I)
p = path_arg(t)
if p.is_dir() or p.stat().st_size > 200_000_000: fail("Give a log file under 200 MB.")
LEVEL = re.compile(r"\b(CRITICAL|FATAL|ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE)\b")
TIME = re.compile(r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2})")
levels, errs, mins, n = collections.Counter(), collections.Counter(), collections.Counter(), 0
with open(p, "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        n += 1
        m = LEVEL.search(line)
        if not m: continue
        lv = m.group(1).replace("WARNING", "WARN"); levels[lv] += 1
        if lv in ("ERROR", "CRITICAL", "FATAL"):
            msg = re.sub(r"\d+", "#", line[m.end():].strip())[:90]            # numbers hidden so similar errors group together
            errs[msg] += 1
            tm = TIME.search(line)
            if tm: mins[tm.group(1)] += 1
print(f"{p.name}: {n:,} lines")
print("Levels: " + (", ".join(f"{k} {v:,}" for k, v in levels.most_common()) or "none recognised"))
if errs:
    print("\nMost common errors:")
    for msg, c in errs.most_common(8): print(f"  {c:>6,}x  {msg}")
if mins:
    print("\nBusiest minutes for errors:")
    for k, c in mins.most_common(3): print(f"  {k}  {c:,}")
