# keywords: mcp call, call mcp tool, use mcp tool, run mcp tool
# desc: Use a tool from a saved MCP server (mcp call files read_file {"path": "notes.txt"}). It runs that server's tool on this computer.
# category: developer
# usage: mcp call <name> <tool> [json arguments]
# confirm: yes
# rawargs: full
# private: yes
# patterns: ^\s*mcp\s+call\b
# priority: 4
import json, re
from _lib import args_text, fail
from _conn import load_reg
import _mcpclient
m = re.match(r"^\s*mcp\s+call\s+([A-Za-z0-9_\-]+)\s+([A-Za-z0-9_.\-]+)\s*(.*)$", args_text(), re.I | re.S)
if not m:
    fail('Usage: mcp call <name> <tool> {"arg": "value"}')
name, tool, raw = m.group(1).lower(), m.group(2), m.group(3).strip()
reg = load_reg("mcp")
if name not in reg:
    fail(f"No server named '{name}'. Saved: {', '.join(sorted(reg)) or 'none'}")
try:
    args = json.loads(raw) if raw else {}
    if not isinstance(args, dict):
        raise ValueError
except ValueError:
    fail("The arguments must be a JSON object, for example {\"path\": \"notes.txt\"}")
try:
    s = _mcpclient.Server(reg[name], timeout=90)
    try:
        res = s.request("tools/call", {"name": tool, "arguments": args})
    finally:
        s.close()
except _mcpclient.MCPError as ex:
    fail(f"'{name}' said: {ex}")
text = "\n".join(c.get("text", "") for c in res.get("content", []) if isinstance(c, dict) and c.get("type") == "text") or json.dumps(res)[:3000]
print(text[:20000])
raise SystemExit(1 if res.get("isError") else 0)
