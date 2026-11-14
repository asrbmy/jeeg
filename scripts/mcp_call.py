# keywords: mcp call, call mcp tool, use mcp tool, run mcp tool
# desc: Use any tool of a saved MCP server (mcp call files write_file {"path": "a.txt", "content": "hi"}). Asks first. Add the word preview to see what would be sent.
# category: developer
# usage: mcp call <name> <tool> [json arguments] [preview]
# confirm: yes
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*mcp\s+call\b
# priority: 4
import json, re
from _lib import args_text, fail
import _mcpclient, _mcpsaved as S, _policy
m = re.match(r"^\s*mcp\s+call\s+([A-Za-z0-9_\-]+)\s+([A-Za-z0-9_.\-]+)\s*(.*)$", args_text(), re.I | re.S)
if not m:
    fail('Usage: mcp call <name> <tool> {"arg": "value"}')
name, tool, raw = m.group(1).lower(), m.group(2), m.group(3).strip()
preview = False
mp = re.search(r"(?:^|\})\s*(?:preview|dry-run|dryrun)\s*$", raw, re.I)
if mp:
    raw, preview = raw[:mp.start() + (1 if raw[mp.start():mp.start() + 1] == "}" else 0)].strip(), True
why = _policy.refuse("mcp:" + name)
if why:
    fail(why)
if name not in S.servers():
    fail(f"No server named '{name}'. Saved: {', '.join(sorted(S.servers())) or 'none'}")
try:
    args = json.loads(raw) if raw else {}
    if not isinstance(args, dict):
        raise ValueError
except ValueError:
    fail("The arguments must be a JSON object, for example {\"path\": \"notes.txt\"}")
if preview:
    print(f"Would ask MCP server {name} to run {tool} with:\n  {json.dumps(args)[:2000]}\nPreview only: nothing was sent.")
    raise SystemExit(0)
try:
    s = S.open_saved(name, 90)
    try:
        res = s.request("tools/call", {"name": tool, "arguments": args})
    finally:
        s.close()
except _mcpclient.MCPError as ex:
    fail(f"'{name}' said: {ex}")
print(S.text_of(res)[:20000])
raise SystemExit(1 if res.get("isError") else 0)
