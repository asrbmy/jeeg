# keywords: json, pretty print json, format json, validate json, beautify json, json file
# desc: Pretty-print and validate a JSON file
# category: utility
# usage: json format <file>
import json
from pathlib import Path
from _lib import args_text, fail
t = args_text().strip('"\'')
p = Path(t).expanduser()
if not t or not p.is_file():
    fail("Usage: json format <file.json>")
try:
    print(json.dumps(json.loads(p.read_text(encoding="utf-8")), indent=2, ensure_ascii=False))
except ValueError as e:
    fail(f"Invalid JSON: {e}")
