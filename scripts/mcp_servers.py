# keywords: mcp servers, mcp add, mcp list, mcp tools, other ai tools, connect to mcp server, external tools
# desc: Let JeeG use tools from other MCP servers (mcp add files = npx some-server, mcp tools files, then: mcp call files <tool> {json})
# category: developer
# usage: mcp add <name> = <command> | mcp list | mcp tools <name> | mcp remove <name>
# rawargs: full
# private: yes
# patterns: ^\s*mcp\s+(add|list|tools|remove|servers)\b ;; \bmcp\s+servers?\b
# priority: 3
import re, shlex
from _lib import args_text, fail
from _conn import load_reg, save_reg, clean_name
import _mcpclient
t = re.sub(r"^\s*mcp\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 1)
cmd = parts[0].lower() if parts else "list"
rest = parts[1] if len(parts) > 1 else ""
reg = load_reg("mcp")
if cmd in {"list", "servers"}:
    print("Saved servers:" if reg else "None saved. Example:  mcp add files = npx -y @modelcontextprotocol/server-filesystem ~/Documents")
    for k, v in sorted(reg.items()):
        print(f"  {k:<12} {' '.join(v)[:90]}")
elif cmd == "add":
    m = re.match(r"^([A-Za-z0-9_\-]+)\s*=\s*(.+)$", rest, re.S)
    if not m:
        fail("Usage: mcp add <name> = <command and arguments>")
    try:
        argv = shlex.split(m.group(2), posix=(__import__("os").name != "nt"))
    except ValueError:
        fail("Could not read that command (check the quotes).")
    if not argv:
        fail("Give the command that starts the server.")
    reg[clean_name(m.group(1))] = argv
    save_reg("mcp", reg)
    print(f"Saved. See what it offers:  mcp tools {m.group(1).lower()}")
elif cmd in {"remove", "delete"}:
    if reg.pop(clean_name(rest.strip()), None) is None:
        fail("No server with that name.")
    save_reg("mcp", reg)
    print("Removed.")
elif cmd == "tools":
    name = clean_name(rest.strip())
    if name not in reg:
        fail(f"No server named '{name}'. Saved: {', '.join(sorted(reg)) or 'none'}")
    try:
        s = _mcpclient.Server(reg[name], timeout=45)
        try:
            tools = s.request("tools/list").get("tools", [])
        finally:
            s.close()
    except _mcpclient.MCPError as ex:
        fail(f"Could not talk to '{name}': {ex}")
    if not tools:
        print("That server offers no tools.")
    for tl in tools[:60]:
        props = ", ".join((tl.get("inputSchema") or {}).get("properties", {}).keys())
        print(f"  {tl.get('name')}({props}): {(tl.get('description') or '')[:90]}")
    print(f"\nCall one:  mcp call {name} <tool> {{\"arg\": \"value\"}}")
else:
    fail("Use:  mcp add | list | tools | remove     and to use a tool:  mcp call <name> <tool> <json>")
