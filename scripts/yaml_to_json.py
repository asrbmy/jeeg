# keywords: yaml to json, convert yaml to json, yml to json, yaml json, make json from yaml
# desc: Convert a YAML file to JSON (yaml to json config.yaml)
# category: developer
# usage: yaml to json <file.yaml>
# rawargs: yes
# patterns: \bya?ml\b.*\b(to|into|2)\b.*\bjson\b
import json, re
from _lib import args_text, fail, need
from _files import path_arg, unique_path
yaml = need("yaml", "pyyaml")
p = path_arg(re.sub(r"^\s*(?:convert\s+)?(?:yaml\s+|yml\s+)?(?:to\s+)?(?:json\s+)?(?:file\s+)?", "", args_text(), flags=re.I))
if p.stat().st_size > 20 * 1024 * 1024: fail("That file is larger than 20 MB.")
try: data = yaml.safe_load(p.read_text(encoding="utf-8-sig"))
except yaml.YAMLError as e: fail(f"Not valid YAML: {e}")
out = unique_path(p.with_suffix(".json"))
out.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
print(f"Saved {out}")
