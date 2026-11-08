# keywords: csv to json, convert csv, csv json, csv into json, csv file to json, turn csv into json
# desc: Convert a CSV file to JSON (csv to json sales.csv). Writes a new .json next to it.
# category: files
# usage: csv to json <file.csv>
# rawargs: full
# patterns: \bcsv\s+(to|into)\s+json\b ;; \b(convert|turn|change)\b.*\bcsv\b.*\bjson\b
# priority: 1
import csv, json, sys
from pathlib import Path
from _lib import args_text, fail, human
from _files import path_arg, unique_path
t = args_text()
p = path_arg(t.replace("csv to json", "").replace("convert", "").strip() or t)
if not p.is_file() or p.stat().st_size > 50 * 1024 * 1024:
    fail("Give a CSV file under 50 MB, e.g. csv to json sales.csv")
csv.field_size_limit(10 * 1024 * 1024)
with open(p, encoding="utf-8-sig", newline="") as fh:
    sample = fh.read(4096)
    fh.seek(0)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.DictReader(fh, dialect=dialect))
def conv(v):
    if v is None:
        return None
    s = v.strip()
    if s == "":
        return None
    try:
        if s.lstrip("-").isdigit() and len(s.lstrip("-")) < 16 and not (len(s) > 1 and s.lstrip("-").startswith("0")):
            return int(s)
        f = float(s)
        if f == f and f not in (float("inf"), float("-inf")) and not s.lower().startswith(("0x", "nan", "inf")):
            return f
    except ValueError:
        pass
    return s
data = [{(k or "").strip(): conv(v) for k, v in r.items() if k is not None} for r in rows]
dest = unique_path(p.with_suffix(".json"))
dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
cols = list(data[0].keys()) if data else []
print(f"Converted {len(data):,} rows, {len(cols)} columns -> {dest}  [{human(dest.stat().st_size)}]")
if cols:
    print("Columns: " + ", ".join(cols[:12]) + (" ..." if len(cols) > 12 else ""))
    print("First row: " + json.dumps(data[0], ensure_ascii=False)[:300])
