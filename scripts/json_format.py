# keywords: json, pretty print json, format json, validate json, beautify json, json file
# desc: Pretty-print and validate a JSON file, or JSON piped in (type data.json | jeeg format json)
# category: utility
# usage: json format <file>
# stdin: yes
import json
from pathlib import Path
from _lib import args_text, fail, stdin_text
t = args_text().strip('"\'')
if t:
    p = Path(t).expanduser()
    if not p.is_file():
        fail("Usage: json format <file.json>   (or pipe JSON in:  type data.json | jeeg format json)")
    raw = p.read_text(encoding="utf-8")
else:
    raw = stdin_text()
    if not raw.strip():
        fail("Usage: json format <file.json>   (or pipe JSON in:  type data.json | jeeg format json)")
try:
    print(json.dumps(json.loads(raw), indent=2, ensure_ascii=False))
except ValueError as e:
    fail(f"Invalid JSON: {e}")
