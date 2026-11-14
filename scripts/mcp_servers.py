# keywords: mcp servers, mcp add, mcp list, mcp catalog, mcp tools, mcp login, mcp mark, other ai tools, connect to mcp server, external tools
# desc: Let JeeG use other MCP servers (mcp catalog, mcp add filesystem ~/Documents, mcp add files = npx some-server, mcp login <name>, mcp tools <name>, mcp mark <name> <tool> read)
# category: developer
# usage: mcp catalog | mcp add <catalog name> [argument] | mcp add <name> = <command or https address> | mcp list | mcp tools <name> | mcp login <name> [ENV_VAR ...] | mcp logout <name> | mcp mark <name> <tool,tool> read|write | mcp remove <name>
# rawargs: full
# private: yes
# network: yes
# patterns: ^\s*mcp\s+(add|list|tools|remove|servers|catalog|login|logout|mark)\b ;; \bmcp\s+servers?\b
# priority: 3
import os, re, shlex, sys
from _lib import args_text, fail
from _conn import ask_secret, clean_name
import _mcpclient, _mcpsaved as S
from _mcpcatalog import CATALOG, JEEG_HAS, REMOTE_ONLY
t = re.sub(r"^\s*mcp\s*", "", args_text(), flags=re.I).strip()
parts = t.split(None, 1)
cmd = parts[0].lower() if parts else "list"
rest = parts[1].strip() if len(parts) > 1 else ""
tty = (sys.stdin is not None and sys.stdin.isatty()) or os.environ.get("JEEG_TEST_TTY") == "1"
if cmd in {"add", "remove", "delete", "login", "logout", "mark"} and not tty:
    fail("Adding servers, logging in and choosing what may be read is done by you, in a terminal window. A program or an AI cannot. Open a terminal and run the same words there.")
sv = S.servers()


def need(name):
    name = clean_name(name)
    if name not in sv:
        fail(f"No server named '{name}'. Saved: {', '.join(sorted(sv)) or 'none'}")
    return name


if cmd in {"list", "servers"}:
    print("Saved servers:" if sv else "None saved. See the ready-made ones:  mcp catalog      or add your own:  mcp add files = npx -y @modelcontextprotocol/server-filesystem ~/Documents")
    for k, v in sorted(sv.items()):
        ev = S.env_name(k)
        login = "" if not ev else ("  logged in" if S.logged_in(k) else "  NEEDS LOGIN")
        kind = "web" if len(v) == 1 and v[0].lower().startswith("http") else "program"
        print(f"  {k:<14} {kind:<8} {len(S.read_tools(k))} tool(s) marked read{login}   {' '.join(v)[:60]}")
elif cmd == "catalog":
    print("Ready-made MCP servers (add with  mcp add <name>). Written from each project's README; not started from here, so check with  mcp tools <name>  after adding:")
    for k, v in sorted(CATALOG.items()):
        print(f"  {k:<16} {'web' if v.get('url') else 'program':<8} {v['note']}" + (f"   needs: {v['arg']}" if v.get("arg") else "") + (f"   login: {v['env'].replace(',', ', ')}" if v.get("env") and v["env"] != "@bearer" else "   (login optional/token)" if v.get("env") else ""))
    print("\nPrograms need Node (npx) or uv (uvx) installed on this computer.")
    print("Not here, because they sign in through the AI app itself: " + REMOTE_ONLY + ".")
    print(JEEG_HAS + ".")
elif cmd == "add":
    m = re.match(r"^([A-Za-z0-9_\-]+)\s*=\s*(.+)$", rest, re.S)
    entry, env, reads = None, "", []
    if m:
        name = clean_name(m.group(1))
        try:
            argv = shlex.split(m.group(2), posix=(os.name != "nt"))
        except ValueError:
            fail("Could not read that command (check the quotes).")
        if not argv:
            fail("Give the command that starts the server, or an https address.")
        if len(argv) == 1 and argv[0].lower().startswith(("http://", "https://")):
            try:
                _mcpclient.HTTPServer._check(argv[0])
            except _mcpclient.MCPError as ex:
                fail(str(ex))
            env = "@bearer"
        elif S.SHELL.match(os.path.basename(argv[0])):
            fail("A shell is not an MCP server. Name the program that is (for example npx or uvx).")
        entry = argv
    else:
        mm = re.match(r"^(?:([A-Za-z0-9_\-]+)\s+from\s+)?([A-Za-z0-9_\-]+)\s*(.*)$", rest, re.S)
        if not mm or mm.group(2).lower() not in CATALOG:
            fail("Usage:  mcp add <catalog name> [argument]     or     mcp add <name> = <command or https address>\nSee the ready-made ones:  mcp catalog")
        cat = CATALOG[mm.group(2).lower()]
        name = clean_name(mm.group(1) or mm.group(2))
        arg = os.path.expanduser(mm.group(3).strip().strip("\"'"))
        if cat.get("url"):
            entry = [cat["url"]]
        else:
            if any("{arg}" in x for x in cat["cmd"]) and not arg:
                fail(f"{mm.group(2)} needs {cat['arg']}:  mcp add {mm.group(2)} <that>")
            entry = [x.replace("{arg}", arg) for x in cat["cmd"]]
        env, reads = cat.get("env", ""), list(cat.get("read", []))
    if name in sv:
        fail(f"There is already a server called {name}. Remove it first:  mcp remove {name}")
    if len(sv) >= 30:
        fail("That is 30 servers already.")
    S.put("mcp", name, entry)
    S.put("mcpenv", name, env or None)
    S.put("mcpread", name, reads or None)
    print(f"Saved {name}." + (f" Log in first:  mcp login {name}" + ("" if env == "@bearer" else "") if env else "") + f"\nSee what it offers:  mcp tools {name}")
    if reads:
        print(f"{len(reads)} tool name(s) are marked as only reading (an AI may use those through  mcp look). Everything else needs your OK.")
elif cmd in {"remove", "delete"}:
    name = need(rest)
    S.drop_logins(name)
    for r in ("mcp", "mcpenv", "mcpread"):
        S.put(r, name, None)
    print("Removed.")
elif cmd == "login":
    w = rest.split()
    if not w:
        fail("Usage: mcp login <name> [ENV_VAR ...]")
    name = need(w[0])
    if len(w) > 1:
        if any(not re.fullmatch(r"[A-Z][A-Z0-9_]{1,60}", x) for x in w[1:]) or len(w) > 7:
            fail("The variable names look like GITHUB_PERSONAL_ACCESS_TOKEN (capital letters, digits, _).")
        S.drop_logins(name)
        S.put("mcpenv", name, ",".join(w[1:]))
    vs = S.env_vars(name)
    if not vs:
        fail(f"{name} has no login variable. Say which one:  mcp login {name} SOME_TOKEN_NAME")
    for v in vs:
        label = "the login" if v == "@bearer" else v
        secret = ask_secret(f"Paste {label} for {name} (it is not shown): ")
        if not secret or re.search(r"[\x00-\x1f\x7f\s]", secret) or len(secret) > 4000:
            fail(f"That does not look right for {label} (no spaces or new lines).")
        S.put("mcpsecrets", name if len(vs) == 1 else f"{name}:{v}", secret)
    print(f"Saved the login for {name} (private to you). It is given to that server only, " + ("as a bearer token." if vs == ["@bearer"] else "in: " + ", ".join(vs) + "."))
elif cmd == "logout":
    name = need(rest)
    S.drop_logins(name)
    print(f"Forgot the login for {name}.")
elif cmd == "mark":
    mm = re.match(r"^([A-Za-z0-9_\-]+)\s+(.+?)\s+(read|write)$", rest, re.I | re.S)
    if not mm:
        fail("Usage: mcp mark <name> <tool,tool> read      (read = it only looks; write = it needs your OK again)")
    name = need(mm.group(1))
    tools = [x for x in re.split(r"[\s,]+", mm.group(2)) if x]
    if not tools or any(not re.fullmatch(r"[A-Za-z0-9_.\-]{1,80}", x) for x in tools):
        fail("Tool names are letters, digits, _ . -")
    cur = S.read_tools(name)
    cur = (cur | set(tools)) if mm.group(3).lower() == "read" else (cur - set(tools))
    S.put("mcpread", name, sorted(cur) or None)
    print(f"{name}: {len(cur)} tool(s) marked read. Only mark a tool read if it really changes nothing.")
elif cmd == "tools":
    name = need(rest)
    try:
        s = S.open_saved(name, 45)
        try:
            tools = s.request("tools/list").get("tools", [])
        finally:
            s.close()
    except _mcpclient.MCPError as ex:
        fail(f"Could not talk to '{name}': {ex}")
    reads = S.read_tools(name)
    if not tools:
        print("That server offers no tools.")
    for tl in tools[:80]:
        props = ", ".join((tl.get("inputSchema") or {}).get("properties", {}).keys())
        print(f"  [{'read ' if tl.get('name') in reads else 'WRITE'}] {tl.get('name')}({props}): {(tl.get('description') or '')[:80]}")
    print(f"\nLook:  mcp look {name} <tool> {{\"arg\": \"value\"}}   (only for [read] tools)\nDo:    mcp call {name} <tool> {{\"arg\": \"value\"}}   (asks first)\nChange which tools only look:  mcp mark {name} <tool> read")
else:
    fail("Use:  mcp catalog | add | list | tools | login | mark | remove     and to use a tool:  mcp look | mcp call <name> <tool> <json>")
