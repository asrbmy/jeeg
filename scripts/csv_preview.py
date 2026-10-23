# keywords: csv preview, preview csv, show csv, view csv, look at csv, csv head, csv columns, open csv in terminal, peek csv
# desc: Show the first rows of a CSV file as a table (csv preview data.csv)
# category: developer
# usage: csv preview <file.csv>
# rawargs: yes
import csv, re
from _lib import args_text, fail
from _files import path_arg
p = path_arg(re.sub(r"^\s*(?:show\s+)?(?:csv\s+)?(?:preview\s+)?(?:of\s+)?(?:file\s+)?", "", args_text(), flags=re.I))
raw = p.read_bytes()[:200000].decode("utf-8-sig", errors="replace")
try: dialect = csv.Sniffer().sniff(raw[:5000], delimiters=",;\t|")
except csv.Error: dialect = csv.excel
rows = []; total = 0
with open(p, newline="", encoding="utf-8-sig", errors="replace") as f:
    for r in csv.reader(f, dialect):
        total += 1
        if total <= 11: rows.append(r)
        if total > 2_000_000: break
if not rows: fail("The file is empty.")
n = max(len(r) for r in rows)
rows = [r + [""] * (n - len(r)) for r in rows]
w_ = [min(22, max(len(str(r[i])) for r in rows)) for i in range(n)]
for i, r in enumerate(rows):
    print("  ".join(str(c)[:22].ljust(w_[j]) for j, c in enumerate(r)))
    if i == 0: print("  ".join("-" * x for x in w_))
print(f"\n{total - 1:,} data rows, {n} columns" + (" (count stopped at 2 million)" if total > 2_000_000 else ""))
