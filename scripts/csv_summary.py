# keywords: csv summary, summarise csv, csv stats, csv statistics, describe csv, analyse csv, csv totals, csv columns summary
# desc: Summarise a CSV: rows, columns, number totals and common values (csv summary data.csv)
# category: developer
# usage: csv summary <file.csv>
# rawargs: full
# priority: 1
import csv, re
from collections import Counter
from _lib import args_text, fail
from _files import path_arg
p = path_arg(re.sub(r"^\s*(?:please\s+)?(?:csv\s+)?(?:summary|summarise|summarize|stats|statistics|describe|analyse|analyze)\s*(?:of\s+)?(?:csv\s+)?(?:file\s+)?", "", args_text(), flags=re.I))
raw = p.read_bytes()[:20_000_000].decode("utf-8-sig", errors="replace")
try: dialect = csv.Sniffer().sniff(raw[:5000], delimiters=",;\t|")
except csv.Error: dialect = csv.excel
rows = list(csv.reader(raw.splitlines(), dialect))
if len(rows) < 2: fail("That file has no data rows.")
head, body = rows[0], rows[1:]
print(f"{p.name}: {len(body):,} rows, {len(head)} columns")
for i, h in enumerate(head):
    col = [r[i].strip() for r in body if i < len(r) and r[i].strip()]
    nums = []
    for v in col:
        try: nums.append(float(v.replace(",", "")))
        except ValueError: break
    blank = len(body) - len(col)
    if col and len(nums) == len(col):
        print(f"  {h}: number  min {min(nums):,.6g}  max {max(nums):,.6g}  sum {sum(nums):,.6g}  mean {sum(nums) / len(nums):,.6g}" + (f"  ({blank} blank)" if blank else ""))
    else:
        top = ", ".join(f"{k} ({n})" for k, n in Counter(col).most_common(3))
        print(f"  {h}: text  {len(set(col))} different  top: {top[:90]}" + (f"  ({blank} blank)" if blank else ""))
