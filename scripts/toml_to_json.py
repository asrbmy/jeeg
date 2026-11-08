# keywords: toml to json, convert toml, toml json, read toml, pyproject json, toml file to json
# desc: Convert a TOML file (such as pyproject.toml) to JSON (toml to json pyproject.toml). Needs Python 3.11 or newer.
# category: developer
# usage: toml to json <file>
# rawargs: full
# patterns: \btoml\s+(to|into)\s+json\b
# priority: 1
import json, sys
from _lib import args_text, fail
from _files import path_arg
try:
    tomllib = __import__("tomllib")
except ImportError:
    fail("Reading TOML needs Python 3.11 or newer (you have " + sys.version.split()[0] + ").")
t = args_text().replace("toml to json", "").replace("convert", "").strip()
p = path_arg(t)
if not p.is_file() or p.stat().st_size > 5 * 1024 * 1024:
    fail("Give a TOML file under 5 MB, e.g. toml to json pyproject.toml")
try:
    data = tomllib.loads(p.read_text(encoding="utf-8"))
except (tomllib.TOMLDecodeError, UnicodeDecodeError) as ex:
    fail(f"Not valid TOML: {ex}")
print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
