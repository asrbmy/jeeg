# keywords: json to csv, convert json to csv, json csv, json file to spreadsheet, export json as csv, flatten json
# desc: Convert a JSON file (a list of records) to CSV (json to csv data.json)
# category: developer
# usage: json to csv <file.json>
# rawargs: yes
import csv, json
from _lib import args_text, fail
from _files import path_arg, unique_path
import re
p = path_arg(re.sub(r"^\s*(?:convert\s+)?(?:json\s+)?(?:to\s+)?(?:csv\s+)?(?:file\s+)?", "", args_text(), flags=re.I))
if p.stat().st_size > 50 * 1024 * 1024: fail("That file is larger than 50 MB.")
try: data = json.loads(p.read_text(encoding="utf-8-sig"))
except (ValueError, UnicodeDecodeError) as e: fail(f"Not valid JSON: {e}")
if isinstance(data, dict):
    lists = [v for v in data.values() if isinstance(v, list) and v and all(isinstance(x, dict) for x in v)]
    data = lists[0] if len(lists) == 1 else [data]
if not isinstance(data, list) or not data or not all(isinstance(x, dict) for x in data):
    fail("The JSON must be a list of records, like [{...}, {...}].")
cols = []
for r in data:
    for k in r:
        if k not in cols: cols.append(k)
out = unique_path(p.with_suffix(".csv"))
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    wr = csv.writer(f); wr.writerow(cols)
    for r in data: wr.writerow([json.dumps(r.get(c), ensure_ascii=False) if isinstance(r.get(c), (dict, list)) else ("" if r.get(c) is None else r.get(c)) for c in cols])
print(f"{len(data)} rows, {len(cols)} columns -> {out}")
