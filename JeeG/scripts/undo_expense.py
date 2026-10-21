# keywords: undo expense, delete last expense, remove last expense, wrong expense, mistake expense, remove expense
# desc: Remove the last recorded expense
# category: money
# confirm: yes
import csv
from _lib import data_dir, fail
f = data_dir() / "expenses.csv"
rows = list(csv.reader(open(f, encoding="utf-8"))) if f.exists() else []
if len(rows) < 2:
    fail("No expenses to remove.")
last = rows.pop()
with open(f, "w", newline="", encoding="utf-8") as fh:
    csv.writer(fh).writerows(rows)
print(f"Removed: {last[0]}  {last[1]}  {last[2]}  {last[3]}")
