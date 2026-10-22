# keywords: json minify, minify json, compact json, shrink json, json one line, compress json
# desc: Shrink a JSON file onto one line (json minify data.json)
# category: developer
# usage: json minify <file.json>
# rawargs: full
# priority: 1
import json, re
from _lib import args_text, fail
from _files import path_arg
p = path_arg(re.sub(r"^\s*(?:please\s+)?(?:json\s+)?(?:minify|compact|shrink)\s*(?:json\s+)?(?:file\s+)?", "", args_text(), flags=re.I))
try: d = json.loads(p.read_text(encoding="utf-8"))
except ValueError as e: fail(f"Invalid JSON: {e}")
out = p.with_name(p.stem + ".min.json")
out.write_text(json.dumps(d, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
print(f"Wrote {out}  ({p.stat().st_size:,} -> {out.stat().st_size:,} bytes)")
