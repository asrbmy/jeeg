# keywords: define variable, store value, remember value as, named value
# desc: Save a value under a name and use it in any phrase as $name (set var rate = 18, then gst 1000 $rate).
# category: utility
# usage: set var <name> = <value>
# rawargs: full
# patterns: ^\s*(set|save|define|store|let)\s+(a\s+)?(var|variable)\b
# priority: 2
import re
from _lib import args_text, fail, var_all, var_save
t = re.sub(r"^\s*(?:set|save|define|store|let)\s+(?:a\s+)?(?:var|variable)\s+", "", args_text(), flags=re.I).strip()
m = re.fullmatch(r"\$?([A-Za-z][A-Za-z0-9_]{0,23})\s*(?:=|:|\bas\b|\bto\b|\bis\b)?\s*(.+)", t, re.S)
if not m:
    fail("Usage: set var <name> = <value>   e.g. set var rate = 18, then:  gst 1000 $rate")
name, value = m.group(1).lower(), m.group(2).strip()
if not value or len(value) > 120 or re.search(r"[\x00-\x1f\x7f]", value):
    fail("The value must be 1-120 characters on one line.")
if name in {"ans"} and not re.fullmatch(r"-?\d+(?:\.\d+)?", value):
    fail("'ans' is the last calculator answer and must be a number.")
vs = var_all()
if name not in vs and len(vs) >= 100:
    fail("You can keep at most 100 variables. Remove some with: remove var <name>")
try:
    vs[name] = float(value) if re.fullmatch(r"-?\d+\.\d+", value) else int(value) if re.fullmatch(r"-?\d{1,15}", value) else value
except ValueError:
    vs[name] = value
var_save(vs)
print(f"${name} = {vs[name]}   (use it in any phrase, for example:  gst 1000 ${name})")
