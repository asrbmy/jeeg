# keywords: export csv, export expenses, export journal, export todos, export habits, export notes, save as csv, download my records, records to excel, export records
# desc: Save one list as a CSV file for Excel (export records expenses | journal | todos | habits | birthdays | notes)
# category: backup
# usage: export records <expenses|journal|todos|habits|birthdays|notes>
# rawargs: yes
import csv, json, re, shutil
from pathlib import Path
from _lib import args_text, data_dir, fail
from _files import unique_path
t = args_text().lower()
kinds = {"expense": "expenses", "journal": "journal", "todo": "todos", "to-do": "todos", "habit": "habits", "birthday": "birthdays", "note": "notes"}
kind = next((v for k, v in kinds.items() if k in t), None)
if not kind: fail("Usage: export records <expenses|journal|todos|habits|birthdays|notes>")
d = data_dir()
out = unique_path(Path.cwd() / f"jeeg_{kind}.csv")
def need(name):
    p = d / name
    if not p.exists(): fail(f"You have no {kind} yet.")
    return p
rows, head = [], []
if kind == "expenses":
    shutil.copy2(need("expenses.csv"), out); print(f"Saved {out}"); raise SystemExit(0)
elif kind == "journal":
    head = ["date", "time", "entry"]
    for l in need("journal.txt").read_text(encoding="utf-8").splitlines():
        m = re.match(r"(\d{4}-\d\d-\d\d) (\d\d:\d\d)\s+(.*)", l)
        if m: rows.append(list(m.groups()))
elif kind == "todos":
    head = ["id", "text", "done", "created"]
    rows = [[i.get("id"), i.get("text"), i.get("done"), i.get("created")] for i in json.loads(need("todos.json").read_text(encoding="utf-8"))]
elif kind == "habits":
    head = ["habit", "date"]
    for h, days in json.loads(need("habits.json").read_text(encoding="utf-8")).items(): rows += [[h, x] for x in days]
elif kind == "birthdays":
    head = ["name", "day_month", "birth_year"]
    for n, v in json.loads(need("birthdays.json").read_text(encoding="utf-8")).items(): rows.append([n, v.get("date"), v.get("year") or ""])
elif kind == "notes":
    head = ["note"]; rows = [[l] for l in need("notes.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.writer(f); wr.writerow(head); wr.writerows(rows)
print(f"{len(rows)} row(s) -> {out}")
