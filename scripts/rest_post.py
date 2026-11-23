# keywords: rest post, post to api, send json to api, api post
# desc: Send JSON to a saved web service (rest post shop /items {"name":"x"}). Asks first. Save the service with: rest add
# category: network
# usage: rest post <name> <path> <json>
# rawargs: full
# network: yes
# confirm: yes
# patterns: ^\s*rest\s+post\b
# priority: 5
import json, re
from _lib import args_text, fail
from _conn import load_reg, clean_name
import _rest
t = re.sub(r"^\s*rest\s+post\s*", "", args_text(), flags=re.I).strip()
p = t.split(None, 2)
if len(p) < 3:
    fail("Usage: rest post <name> <path> <json>")
try:
    body = json.loads(p[2])
except ValueError:
    fail("The data must be JSON.")
st, raw = _rest.request(load_reg("rest"), clean_name(p[0]), "POST", p[1], body)
print(f"HTTP {st}\n" + raw[:3000])
