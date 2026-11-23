# keywords: audit log, audit export, activity log, what did jeeg run, what ran, run history export, ai activity
# desc: See and export what JeeG ran and who asked (you or an AI): audit show 20, audit summary, audit export. Task names and results only, never what you typed.
# category: security
# usage: audit show [n] | audit summary | audit ai | audit export [file.csv]
# rawargs: full
# patterns: ^\s*audit\b ;; ^\s*(what|which tasks?)\s+did\s+(an\s+)?(ai|jeeg)\s+(run|do)\b
# priority: 4
import csv, datetime, json, re
from collections import Counter
from pathlib import Path
from _lib import args_text, data_dir, fail, output_dir
t = re.sub(r"^\s*audit\s*", "", args_text(), flags=re.I).strip().lower()
f = data_dir() / "log.jsonl"
rows = []
if f.exists():
    for ln in f.read_text(encoding="utf-8", errors="replace").splitlines()[-100000:]:
        try:
            d = json.loads(ln)
            rows.append({"time": datetime.datetime.fromtimestamp(int(d["t"])).strftime("%Y-%m-%d %H:%M:%S"), "task": str(d["s"]).replace("_", " "),
                         "result": "ok" if d.get("rc") == 0 else f"exit {d.get('rc')}", "seconds": d.get("dt", 0), "asked_by": ("rule:" + str(d["bridge"])) if d.get("bridge") else ("computer:" + str(d["peer"])) if d.get("peer") else ("AI" if d.get("ai") else "you")})
        except (ValueError, KeyError, TypeError):
            continue
if not rows:
    fail("Nothing has been logged yet (or logging is off: --no-log / JEEG_NOLOG).")
sub = t.split()[0] if t else "show"
if sub == "export":
    arg = t[len("export"):].strip().strip("\"'")
    p = Path(arg).expanduser() if arg else output_dir("JeeG audit") / f"audit-{datetime.date.today():%Y%m%d}.csv"
    if p.suffix.lower() != ".csv": fail("Name the file with .csv, or leave the name out.")
    if p.exists() and arg: fail(f"{p} already exists; choose another name.")
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["time", "task", "result", "seconds", "asked_by"]); w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} row(s) to {p}. It lists task names and results only; what you typed is never logged.")
elif sub == "summary":
    c = Counter((r["task"], r["asked_by"]) for r in rows)
    print(f"{len(rows)} run(s); {sum(1 for r in rows if r['asked_by'] == 'AI')} asked for by an AI; {sum(1 for r in rows if r['result'] != 'ok')} did not succeed.")
    for (task, who), n in c.most_common(10): print(f"  {n:>4}  {task}  ({who})")
elif sub in {"show", "ai"} or sub.isdigit():
    n = int(sub) if sub.isdigit() else (int(t.split()[1]) if sub == "show" and len(t.split()) > 1 and t.split()[1].isdigit() else 20)
    sel = [r for r in rows if sub != "ai" or r["asked_by"] != "you"][-min(n, 200):]
    if not sel: fail("No runs asked for by an AI are logged.")
    for r in sel: print(f"  {r['time']}  {r['asked_by']:<4} {r['task']:<26}{r['result']}")
else:
    fail("Say: audit show [n] | audit summary | audit ai | audit export [file.csv]")
