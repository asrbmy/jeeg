# keywords: json to yaml, convert json to yaml, json yaml, make yaml from json, config to yaml
# desc: Convert a JSON file to YAML (json to yaml config.json)
# category: developer
# usage: json to yaml <file.json>
# rawargs: yes
# patterns: \bjson\b.*\b(to|into|2)\b.*\bya?ml\b
import json, re
from _lib import args_text, fail, need
from _files import path_arg, unique_path
yaml = need("yaml", "pyyaml")
p = path_arg(re.sub(r"^\s*(?:convert\s+)?(?:json\s+)?(?:to\s+)?(?:yaml\s+)?(?:file\s+)?", "", args_text(), flags=re.I))
if p.stat().st_size > 20 * 1024 * 1024: fail("That file is larger than 20 MB.")
try: data = json.loads(p.read_text(encoding="utf-8-sig"))
except ValueError as e: fail(f"Not valid JSON: {e}")
out = unique_path(p.with_suffix(".yaml"))
out.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
print(f"Saved {out}")
